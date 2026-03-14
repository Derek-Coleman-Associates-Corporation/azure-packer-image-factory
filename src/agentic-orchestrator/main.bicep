@description('The name of the Azure Function App')
param functionAppName string = 'func-agentic-orchestrator-${uniqueString(resourceGroup().id)}'

@description('The region for deployment')
param location string = resourceGroup().location

@description('Storage Account name required by Azure Functions')
param storageAccountName string = 'stagentic${uniqueString(resourceGroup().id)}'

@description('The secret cryptographic key extracted from GitHub App Webhook Settings')
@secure()
param githubWebhookSecret string

@description('The URI Endpoint for your Azure AI / Antigravity Agentic Framework worker')
param agentApiEndpoint string

@description('The secure access key for the Agentic Framework worker API')
@secure()
param agentApiKey string

var hostingPlanName = 'plan-${functionAppName}'
var applicationInsightsName = 'appi-${functionAppName}'

// Azure Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    defaultToOAuthAuthentication: true
  }
}

// Dedicated App Service Plan (Consumption Linux)
resource hostingPlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: hostingPlanName
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  properties: {
    reserved: true // Required for Linux hosting
  }
}

// Application Insights
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Request_Source: 'rest'
  }
}

// Function App
resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: hostingPlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTAZUREFILECONNECTIONSTRING'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};EndpointSuffix=${environment().suffixes.storage};AccountKey=${storageAccount.listKeys().keys[0].value}'
        }
        {
          name: 'WEBSITE_CONTENTSHARE'
          value: toLower(functionAppName)
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: applicationInsights.properties.InstrumentationKey
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'GITHUB_WEBHOOK_SECRET'
          value: githubWebhookSecret
        }
        {
          name: 'AGENT_API_ENDPOINT'
          value: agentApiEndpoint
        }
        {
          name: 'AGENT_API_KEY'
          value: agentApiKey
        }
      ]
    }
  }
}

output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}/api/github-webhook-trigger'
output functionAppName string = functionApp.name
