"""
S3 Vector Bucket CDK Construct
Creates and manages S3 Vector buckets and indexes for vector search functionality.
"""
from aws_cdk import (
    CfnOutput,
    aws_s3vectors as s3vectors,
    aws_iam as iam,
)
from constructs import Construct
from typing import Optional, List


class S3VectorBucket(Construct):
    """
    CDK Construct for S3 Vector bucket with support for multiple indexes.
    Allows other stacks to add indexes to the same bucket.
    """
    
    def __init__(
        self, 
        scope: Construct, 
        construct_id: str,
        bucket_name: str,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        self.bucket_name = bucket_name
        
        # Create S3 Vector bucket
        self.vector_bucket = s3vectors.CfnVectorBucket(
            self,
            "VectorBucket",
            vector_bucket_name=bucket_name
        )
        
        # Store bucket ARN for cross-stack references
        self.bucket_arn = self.vector_bucket.attr_arn
        
        # Output bucket details for other stacks
        CfnOutput(
            self,
            "VectorBucketName",
            value=self.vector_bucket.vector_bucket_name,
            export_name=f"{bucket_name}-VectorBucketName"
        )
        
        CfnOutput(
            self,
            "VectorBucketArn", 
            value=self.bucket_arn,
            export_name=f"{bucket_name}-VectorBucketArn"
        )
    
    def add_index(
        self,
        index_name: str,
        dimension: int = 1024,
        distance_metric: str = "cosine",
        data_type: str = "float32",
        **kwargs
    ) -> s3vectors.CfnIndex:
        """
        Add a vector index to this bucket.
        
        Args:
            index_name: Name of the vector index
            dimension: Vector dimension (default: 1024 for Bedrock Titan)
            distance_metric: Distance metric (cosine or euclidean)
            data_type: Vector data type (float32)
            
        Returns:
            CfnIndex: The created index construct
        """
        index = s3vectors.CfnIndex(
            self,
            f"Index-{index_name}",
            vector_bucket_name=self.vector_bucket.vector_bucket_name,
            index_name=index_name,
            dimension=dimension,
            distance_metric=distance_metric,
            data_type=data_type,
            **kwargs
        )
        
        # Index depends on bucket
        index.add_dependency(self.vector_bucket)
        
        # Output index details
        CfnOutput(
            self,
            f"IndexArn-{index_name}",
            value=index.attr_arn,
            export_name=f"{self.bucket_name}-{index_name}-IndexArn"
        )
        
        return index


class S3VectorIndex(Construct):
    """
    Standalone S3 Vector Index construct for adding indexes to existing buckets.
    Use this when the bucket is created in another stack.
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucket_name: str,
        index_name: str,
        dimension: int = 1024,
        distance_metric: str = "cosine",
        data_type: str = "float32",
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        self.bucket_name = bucket_name
        self.index_name = index_name
        
        # Create index in existing bucket
        self.index = s3vectors.CfnIndex(
            self,
            "VectorIndex",
            vector_bucket_name=bucket_name,
            index_name=index_name,
            dimension=dimension,
            distance_metric=distance_metric,
            data_type=data_type,
            **kwargs
        )
        
        # Output index details
        CfnOutput(
            self,
            "IndexArn",
            value=self.index.attr_arn,
            export_name=f"{bucket_name}-{index_name}-IndexArn"
        )
        
        CfnOutput(
            self,
            "IndexName",
            value=self.index.index_name,
            export_name=f"{bucket_name}-{index_name}-IndexName"
        )


def create_vector_permissions(bucket_name: str, index_names: Optional[List[str]] = None) -> iam.PolicyDocument:
    """
    Create IAM policy for S3 Vector operations.
    
    Args:
        bucket_name: S3 Vector bucket name
        index_names: List of index names (optional, grants access to all if None)
        
    Returns:
        IAM PolicyDocument for S3 Vector permissions
    """
    bucket_arn = f"arn:aws:s3vectors:*:*:vector-bucket/{bucket_name}"
    
    # Base permissions for bucket operations
    statements = [
        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3vectors:GetVectorBucket",
                "s3vectors:ListIndexes"
            ],
            resources=[bucket_arn]
        )
    ]
    
    # Index-specific permissions
    if index_names:
        for index_name in index_names:
            index_arn = f"{bucket_arn}/index/{index_name}"
            statements.append(
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3vectors:GetIndex",
                        "s3vectors:PutVectors",
                        "s3vectors:GetVectors", 
                        "s3vectors:QueryVectors",
                        "s3vectors:ListVectors",
                        "s3vectors:DeleteVectors"
                    ],
                    resources=[index_arn]
                )
            )
    else:
        # Grant access to all indexes in bucket
        statements.append(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3vectors:GetIndex",
                    "s3vectors:PutVectors", 
                    "s3vectors:GetVectors",
                    "s3vectors:QueryVectors",
                    "s3vectors:ListVectors",
                    "s3vectors:DeleteVectors"
                ],
                resources=[f"{bucket_arn}/index/*"]
            )
        )
    
    return iam.PolicyDocument(statements=statements)
