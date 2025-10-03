import logging
import s3fs
from sagemaker import Model, PipelineModel
from sagemaker.automl.automlv2 import (
    AutoMLV2,
    AutoMLTimeSeriesForecastingConfig,
    AutoMLDataChannel,
)
from sagemaker.automl.candidate_estimator import CandidateEstimator
from sagemaker.transformer import Transformer
from datetime import datetime
import pandas as pd


logger = logging.getLogger(__name__)


class SageMakerTimeSeriesAutopilot:
    def __init__(self, job_name: str, train_data_s3_uri: str, role_arn: str):
        if job_name is None:
            now = datetime.now().strftime("%Y%m%d-%H%M")
            job_name = f"autopilot-{now}"

        self.job_name = job_name
        self.train_data_s3_uri = train_data_s3_uri
        self.role_arn = role_arn
        self.best_candidate = None
        self.list_candidates = None

    def train(
        self,
        model_output_s3_uri: str,
        forecast_horizon=7,
        target_col="sales",
        series_identifier_col="series_id",
        timestamp_col="date",
        max_runtime_per_training_job_s=600,
        max_total_job_runtime_s=3600,
    ):
        logger.info(f"[{self.job_name}] Starting training job")

        # Configure timeseries
        cfg = AutoMLTimeSeriesForecastingConfig(
            forecast_frequency="D",
            forecast_horizon=forecast_horizon,
            forecast_quantiles=["p10", "p50", "p90"],
            target_attribute_name=target_col,
            timestamp_attribute_name=timestamp_col,
            item_identifier_attribute_name=series_identifier_col,
            # grouping_attribute_names=["store"],
            max_candidates=1,
            max_runtime_per_training_job_in_seconds=max_runtime_per_training_job_s,
            max_total_job_runtime_in_seconds=max_total_job_runtime_s,
        )

        # Configure AutoMLv2 job
        automlv2 = AutoMLV2(
            problem_config=cfg,
            base_job_name=self.job_name,
            role=self.role_arn,
            output_path=model_output_s3_uri,
        )

        # Fit the data (takes about 30 minutes)
        automlv2.fit(
            inputs=[
                AutoMLDataChannel(
                    s3_data_type="S3Prefix",
                    s3_uri=self.train_data_s3_uri,
                    channel_type="training",
                    content_type="text/csv;header=present",
                )
            ],
            wait=True,
            logs=True,
        )

        logger.info(f"[{self.job_name}] Training finished")

        self.best_candidate = automlv2.best_candidate()
        self.list_candidates = automlv2.list_candidates()

        logger.info(f"[{self.job_name}] Best candidate: {self.best_candidate}")

    def register_best_candidate(
        self,
        model_name=None,
        vpc_config=None,
        enable_network_isolation=False,
        model_kms_key=None,
        predictor_cls=None,
        instance_type="ml.m5.xlarge",
    ):
        assert self.best_candidate is not None, "No best candidate found"
        candidate = CandidateEstimator(self.best_candidate)

        if model_name is None:
            model_name = candidate.name

        inference_containers = candidate.containers

        models = []

        for container in inference_containers:
            model = Model(
                image_uri=container["Image"],
                model_data=container["ModelDataUrl"],
                role=self.role_arn,
                env=container["Environment"],
                vpc_config=vpc_config,
                enable_network_isolation=enable_network_isolation,
                model_kms_key=model_kms_key,
            )
            models.append(model)

        pipeline_model = PipelineModel(
            models=models,
            role=self.role_arn,
            predictor_cls=predictor_cls,
            name=model_name,
            vpc_config=vpc_config,
            enable_network_isolation=enable_network_isolation,
        )

        pipeline_model.create(instance_type=instance_type)
        logger.info(f"Registered PipelineModel: {model_name}")

        return pipeline_model

    def predict_batch(
        self,
        model_name: str,
        s3_uri_inference: str,
        s3_uri_output: str,
        instance_count: int = 1,
        instance_type="ml.m5.xlarge",
    ) -> pd.DataFrame:
        logger.info(
            f"Starting batch transform job using best candidate: {model_name}. Source: {s3_uri_inference}. Destination: {s3_uri_output}"
        )

        # Create batch transformer
        transformer = Transformer(
            model_name=model_name,
            instance_count=instance_count,
            instance_type=instance_type,
            output_path=s3_uri_output,
            # strategy="SingleRecord",
            # max_concurrent_transforms=1,
        )

        transformer.transform(
            data=s3_uri_inference,
            content_type="text/csv;header=present",
            split_type="Line",
            wait=True,
            logs=False,
        )

        logger.info("Batch Transform finished")


def get_candidates_performance(
    candidates,
    desired_metrics=["AverageWeightedQuantileLoss", "MASE", "WAPE", "MAPE", "RMSE"],
) -> pd.DataFrame:
    def _map_model_name(candidate_name: str) -> str:
        if "deepar" in candidate_name.lower():
            return "DeepAR"
        elif "cnnqr" in candidate_name.lower():
            return "CNN-QR"
        elif "tsnpts" in candidate_name.lower():
            return "NPTS"
        elif "tsets" in candidate_name.lower():
            return "ETS"
        elif "tsarima" in candidate_name.lower():
            return "ARIMA"
        elif "tsprophet" in candidate_name.lower():
            return "Prophet"
        elif "-me-" in candidate_name.lower() or "ensemble" in candidate_name.lower():
            return "Ensemble"
        else:
            return "Unknown"

    rows = []
    for c in candidates:
        name = _map_model_name(c["CandidateName"])
        metrics = {
            m["MetricName"]: m["Value"]
            for m in c["CandidateProperties"]["CandidateMetrics"]
        }
        row = {"Model": name}
        for m in desired_metrics:
            row[m] = metrics.get(m, None)
        rows.append(row)

    df = pd.DataFrame(rows)
    df.set_index("Model", inplace=True)
    df = df.rename(columns={"AverageWeightedQuantileLoss": "WQL"})

    return df
