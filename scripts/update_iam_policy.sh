#!/usr/bin/env bash
set -e

# Arguments: POLICY_NAME ROLE_NAME POLICY_FILE
POLICY_NAME=$1
ROLE_NAME=$2
POLICY_FILE=$3

POLICY_ARN="arn:aws:iam::283674368847:policy/${POLICY_NAME}"

echo "🔄 Force updating ${POLICY_NAME} policy..."

# Force cleanup - ignore errors and handle multiple versions
echo "🧹 Cleaning up existing policy..."

# Detach from role (ignore if not attached)
aws iam detach-role-policy --role-name ${ROLE_NAME} --policy-arn ${POLICY_ARN} 2>/dev/null || true

# Delete all non-default versions first (handles multiple version issue)
aws iam list-policy-versions --policy-arn ${POLICY_ARN} 2>/dev/null | \
    jq -r '.Versions[] | select(.IsDefaultVersion == false) | .VersionId' 2>/dev/null | \
    xargs -I {} aws iam delete-policy-version --policy-arn ${POLICY_ARN} --version-id {} 2>/dev/null || true

# Delete the policy itself
aws iam delete-policy --policy-arn ${POLICY_ARN} 2>/dev/null || true

echo "📋 Creating fresh policy..."

# Create new policy
aws iam create-policy \
    --policy-name ${POLICY_NAME} \
    --policy-document file://${POLICY_FILE}

# Attach to role
aws iam attach-role-policy \
    --role-name ${ROLE_NAME} \
    --policy-arn ${POLICY_ARN}

echo "✅ ${POLICY_NAME} policy updated successfully!"
