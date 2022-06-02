provider "aws" {
    region = "{AWS::region}"
}

resource "aws_rds_cluster" "amsv2" {
    cluster_identifier = "auroralab-serverlessv2-cluster"
    engine             = "{engine}"
    engine_mode        = "provisioned"
    engine_version     = "{engine_version}"
    database_name      = "myshop"
    master_username    = "{master_username}"
    master_password    = "{master_password}"
    db_subnet_group_name = "{db_subnet_group_name}"
    db_cluster_parameter_group_name = "{db_cluster_parameter_group_name}"
    iam_roles = ["{aurorlabrole}"]
    vpc_security_group_ids = ["{vpc_security_group_ids}"]
    backup_retention_period = 1
    storage_encrypted = true
    enabled_cloudwatch_logs_exports= ["error", "slowquery"]
    iam_database_authentication_enabled = true
    serverlessv2_scaling_configuration {
    max_capacity = 9
    min_capacity = 0.5
    }
    tags = {Key = "Name", Value = "auroralab-serverlessv2-cluster"}
}

resource "aws_rds_cluster_instance" "amsv2" {
  count = 2
  identifier = "auroralab-serverless-node-${count.index}"        
  cluster_identifier = aws_rds_cluster.amsv2.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.amsv2.engine
  engine_version     = aws_rds_cluster.amsv2.engine_version
  monitoring_role_arn = "{monitoring_role_arn}"
  monitoring_interval = 60
  copy_tags_to_snapshot = true
  performance_insights_enabled = true
  performance_insights_retention_period = 7
}