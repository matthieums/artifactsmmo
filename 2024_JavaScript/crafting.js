
import urlBuilder from "./urlBuilder.js";
import requestOptionsBuilder from "./requestOptionsBuilder.js";
import { getCharacterInventory } from "./inventory.js";

export default async function getNecessaryResourcesToCraft(item, amount) {
    // Needs to be further developed. If my character has some part of the item
    // he should not get all the necessary resources from the bank, but just the missing part
    const recipe  = await getItemRecipe(item);
    const enoughMaterial = await characterHasEnoughMaterialFor(recipe, amount)
  
    if (!enoughMaterial) {
      for (const { code, quantity } of recipe) {
        await withdraw(code, quantity * amount);
      }
    }
    return;
  }


async function getItemRecipe(item) {
    
    try {
        const url = urlBuilder.getItemUrl(item)
        const requestOptions = requestOptionsBuilder.buildGetRequestOptions()
        const response = await fetch(url, requestOptions)

      if(!response.ok) {
        handleErrorCode(response.status)
      }

      const data = await response.json()

      return data.data.craft.items;

    } catch (error) {
      throw new Error(error)
    }
  }
  
  
async function characterHasEnoughMaterialFor(items, amount) {

    const inventory = await getCharacterInventory();

    // Check if I have enough material for the amount
    // of items I want to craft

    for (let item of items) {
        let code = item.code
        const requiredQuantity = item.quantity * amount;
        if (!inventory[code] || inventory[code] < requiredQuantity) {
            return false;
        }
    }
    return true;
}
