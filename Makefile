
create-infra:
	aws cloudformation create-stack --stack-name biothings-farm --disable-rollback --template-body file://aws/cloudformation/cloudformation_biothings-farm.template

delete-infra:
	aws cloudformation delete-stack --stack-name biothings-farm

create-api:
	aws cloudformation create-stack --stack-name biothings-farm-api --disable-rollback --template-body file://aws/cloudformation/cloudformation_apigateway.template --parameters ParameterKey=VPCLinkId,ParameterValue=$$VPCLINKID

delete-api:
	aws cloudformation delete-stack --stack-name biothings-farm-api
