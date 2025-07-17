# API Documentation

## Overview

The MCP Azure DevOps Server provides a set of tools for interacting with Azure DevOps variable groups and service connections through the Model Context Protocol (MCP).

## Authentication

The server uses Azure DevOps Personal Access Tokens (PAT) for authentication. You need to create a PAT with the following scopes:

- **Variable Groups (read)**: Required for variable group operations
- **Service Connections (read)**: Required for service connection operations
- **Project and Team (read)**: Required for project validation

## Available Tools

### 1. list_variable_groups

List all variable groups in an Azure DevOps project.

**Input Schema:**

```json
{
  "type": "object",
  "properties": {
    "project": {
      "type": "string",
      "description": "Project name or ID"
    },
    "group_name": {
      "type": "string",
      "description": "Filter by group name (optional)"
    }
  },
  "required": ["project"]
}
```

**Example Request:**

```json
{
  "project": "MyProject",
  "group_name": "Production"
}
```

**Example Response:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "Found 2 variable group(s) in project 'MyProject'"
    },
    {
      "type": "text",
      "text": "[\n  {\n    \"id\": 1,\n    \"name\": \"Production\",\n    \"description\": \"Production environment variables\",\n    \"type\": \"Vsts\",\n    \"variable_count\": 5,\n    \"secret_count\": 2,\n    \"created_by\": \"John Doe\",\n    \"created_on\": \"2023-01-01T12:00:00+00:00\",\n    \"modified_by\": \"Jane Smith\",\n    \"modified_on\": \"2023-01-02T12:00:00+00:00\"\n  }\n]"
    }
  ]
}
```

### 2. get_variable_group_details

Get detailed information about a specific variable group.

**Input Schema:**

```json
{
  "type": "object",
  "properties": {
    "project": {
      "type": "string",
      "description": "Project name or ID"
    },
    "group_id": {
      "type": "integer",
      "description": "Variable group ID"
    }
  },
  "required": ["project", "group_id"]
}
```

**Example Request:**

```json
{
  "project": "MyProject",
  "group_id": 1
}
```

**Example Response:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "Variable group 'Production' details"
    },
    {
      "type": "text",
      "text": "{\n  \"id\": 1,\n  \"name\": \"Production\",\n  \"description\": \"Production environment variables\",\n  \"type\": \"Vsts\",\n  \"variables\": [\n    {\n      \"name\": \"API_URL\",\n      \"value\": \"https://api.example.com\",\n      \"is_secret\": false,\n      \"is_readonly\": false\n    },\n    {\n      \"name\": \"API_KEY\",\n      \"value\": \"[HIDDEN]\",\n      \"is_secret\": true,\n      \"is_readonly\": false\n    }\n  ],\n  \"created_by\": {\n    \"display_name\": \"John Doe\",\n    \"unique_name\": \"john.doe@example.com\"\n  },\n  \"created_on\": \"2023-01-01T12:00:00+00:00\",\n  \"modified_by\": {\n    \"display_name\": \"Jane Smith\",\n    \"unique_name\": \"jane.smith@example.com\"\n  },\n  \"modified_on\": \"2023-01-02T12:00:00+00:00\",\n  \"project_id\": \"proj1\",\n  \"project_name\": \"MyProject\"\n}"
    }
  ]
}
```

### 3. list_service_connections

List all service connections in an Azure DevOps project.

**Input Schema:**

```json
{
  "type": "object",
  "properties": {
    "project": {
      "type": "string",
      "description": "Project name or ID"
    },
    "type": {
      "type": "string",
      "description": "Filter by connection type (optional)"
    },
    "include_shared": {
      "type": "boolean",
      "description": "Include shared connections",
      "default": true
    }
  },
  "required": ["project"]
}
```

**Example Request:**

```json
{
  "project": "MyProject",
  "type": "azurerm",
  "include_shared": true
}
```

**Example Response:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "Found 1 service connection(s) in project 'MyProject' of type 'azurerm'"
    },
    {
      "type": "text",
      "text": "[\n  {\n    \"id\": \"conn1\",\n    \"name\": \"Azure Production\",\n    \"type\": \"azurerm\",\n    \"url\": \"https://management.azure.com/\",\n    \"description\": \"Azure Resource Manager connection for production\",\n    \"is_shared\": false,\n    \"is_ready\": true,\n    \"owner\": \"Library\",\n    \"authorization_scheme\": \"ServicePrincipal\",\n    \"created_by\": \"John Doe\",\n    \"project_name\": \"MyProject\"\n  }\n]"
    }
  ]
}
```

### 4. get_service_connection_details

Get detailed information about a specific service connection.

**Input Schema:**

```json
{
  "type": "object",
  "properties": {
    "project": {
      "type": "string",
      "description": "Project name or ID"
    },
    "connection_id": {
      "type": "string",
      "description": "Service connection ID"
    }
  },
  "required": ["project", "connection_id"]
}
```

**Example Request:**

```json
{
  "project": "MyProject",
  "connection_id": "conn1"
}
```

**Example Response:**

```json
{
  "content": [
    {
      "type": "text",
      "text": "Service connection 'Azure Production' details"
    },
    {
      "type": "text",
      "text": "{\n  \"id\": \"conn1\",\n  \"name\": \"Azure Production\",\n  \"type\": \"azurerm\",\n  \"url\": \"https://management.azure.com/\",\n  \"description\": \"Azure Resource Manager connection for production\",\n  \"is_shared\": false,\n  \"is_ready\": true,\n  \"owner\": \"Library\",\n  \"authorization\": {\n    \"scheme\": \"ServicePrincipal\",\n    \"parameters\": {\n      \"tenantid\": \"[HIDDEN]\",\n      \"serviceprincipalid\": \"[HIDDEN]\"\n    }\n  },\n  \"created_by\": {\n    \"display_name\": \"John Doe\",\n    \"unique_name\": \"john.doe@example.com\"\n  },\n  \"project_id\": \"proj1\",\n  \"project_name\": \"MyProject\",\n  \"data_keys\": [\"subscriptionId\", \"subscriptionName\"]\n}"
    }
  ]
}
```

## Error Handling

All tools return structured error responses when something goes wrong:

```json
{
  "content": [
    {
      "type": "text",
      "text": "Error: Project 'NonExistentProject' not found"
    },
    {
      "type": "text",
      "text": "Details: The project was not found in the organization"
    }
  ],
  "isError": true
}
```

## Rate Limiting

The server respects Azure DevOps API rate limits. If you encounter rate limiting errors, the server will include retry guidance in the error message.

## Security Notes

- Secret values in variable groups are always shown as `[HIDDEN]`
- Service connection authorization parameters are always shown as `[HIDDEN]`
- All API calls are logged for audit purposes
- Personal Access Tokens are never logged or exposed
