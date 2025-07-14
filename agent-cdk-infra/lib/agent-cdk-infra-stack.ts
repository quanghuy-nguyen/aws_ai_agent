import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DockerImageFunction,
        DockerImageCode,
        FunctionUrlAuthType,
        Architecture, 
        FunctionUrl,
      } from 'aws-cdk-lib/aws-lambda';
import { platform } from 'os';

export class AgentCdkInfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Lambda function for api
    const apiImageCode = DockerImageCode.fromImageAsset('../image', {
      cmd: ["app_api_handler.handler"],
      buildArgs: {
        platform: "linux/amd64",
      },
    });

    const apiFunction = new DockerImageFunction(this, 'AgentApiFunction', {
      code: apiImageCode,
      architecture: Architecture.X86_64,
      memorySize: 512,
      timeout: cdk.Duration.seconds(60),
    });


    // Create a function URL for the API Lambda function
    const functionUrl = apiFunction.addFunctionUrl({
      authType: FunctionUrlAuthType.NONE, // No authentication for simplicity
    });
    

    // Output the function URL
    new cdk.CfnOutput(this, 'FunctionUrl', {
      value: functionUrl.url,
      description: 'The URL of the Lambda function',
    });
  }
}
