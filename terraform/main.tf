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

# ----------------------------
# Resource Group
# ----------------------------
data "azurerm_resource_group" "rg" {
  name = "VisualStudioOnline-B7676031D19941C29CB021209999B63D"
}

# ----------------------------
# ACR
# ----------------------------
data "azurerm_container_registry" "acr" {
  name                = "corvitrojectacr"
  resource_group_name = data.azurerm_resource_group.rg.name
}

# ----------------------------
# Virtual Network (/16)
# ----------------------------
resource "azurerm_virtual_network" "vnet" {
  name                = "corvit-vnet"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  address_space       = ["10.0.0.0/16"]
}

# ----------------------------
# Public Subnet (/24)
# ----------------------------
resource "azurerm_subnet" "public_subnet" {
  name                 = "public-subnet"
  resource_group_name  = data.azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

# ----------------------------
# Private Subnet (/24)
# ----------------------------
resource "azurerm_subnet" "private_subnet" {
  name                 = "private-subnet"
  resource_group_name  = data.azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.2.0/24"]
}

# ----------------------------
# AKS Cluster (in private subnet)
# ----------------------------
resource "azurerm_kubernetes_cluster" "aks" {
  name                = "lms-aks-cluster"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  dns_prefix          = "corvitaks"
  node_resource_group = "corvit-aks-nodes"

  default_node_pool {
    name           = "default"
    node_count     = 1
    vm_size        = "Standard_D2s_v3"
    vnet_subnet_id = azurerm_subnet.private_subnet.id
  }

  identity {
    type = "SystemAssigned"
  }
  network_profile {
    network_plugin = "azure"
    service_cidr   = "172.20.0.0/16"
    dns_service_ip = "172.20.0.10"
  }
}

# ----------------------------
# AKS → ACR Access
# ----------------------------
resource "azurerm_role_assignment" "aks_acr" {
  principal_id         = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name = "AcrPull"
  scope                = data.azurerm_container_registry.acr.id
}
