terraform {
  required_version = ">= 1.3"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 5.3"
    }
  }

  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}