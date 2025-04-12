import requestOptionsBuilder from "./requestOptionsBuilder.js"
import urlBuilder from "./urlBuilder.js"

async function getCharacterInventory() {
  try {  
    const url = urlBuilder.getCharactersUrl();
    const requestOptions = requestOptionsBuilder.buildGetRequestOptions();

    const response = await fetch(url, requestOptions)

    if (!response.ok) {
      handleErrorCode(response.status)
    }

    const { data: [{ inventory }] } = await response.json();
    const inventoryItems = extractIndividualInventorySlots(inventory);
    
    return inventoryItems;

  } catch (error) {
  throw new Error(error)
  }
}
  
function extractIndividualInventorySlots(inventory) {
  let slotsContent = {}
  for (let slot of inventory) {
    slotsContent[slot.code] = slot.quantity
  }
  return slotsContent
}

export {
  getCharacterInventory,
  extractIndividualInventorySlots
};