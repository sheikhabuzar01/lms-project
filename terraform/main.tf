terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Get existing Resource Group
data "azurerm_resource_group" "rg" {
  name = "VisualStudioOnline-B7676031D19941C29CB021209999B63D"
}

# Get existing ACR
data "azurerm_container_registry" "acr" {
  name                = "corvitprojectacr"
  resource_group_name = "VisualStudioOnline-B7676031D19941C29CB021209999B63D"
}

# Create AKS Cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "corvit-aks-cluster"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  dns_prefix          = "corvitaks"
  node_resource_group = "corvit-aks-nodes" 

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_D2s_v3"
  }

  identity {
    type = "SystemAssigned"
  }
}

# Connect AKS to ACR
resource "azurerm_role_assignment" "aks_acr" {
  principal_id                     = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = data.azurerm_container_registry.acr.id
  skip_service_principal_aad_check = true
}