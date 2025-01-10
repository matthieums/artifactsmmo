export async function getCharacterInventory() {
    try {  
    const url = `${server}/my/characters/`
    requestOptions = switchToGetRequest(requestOptions)
    const response = await fetch(url, requestOptions)
    if (!response.ok) {
      handleErrorCode(response.status)
    }
    const characterData = await response.json()
    const inventory = characterData.data[0].inventory
    const inventoryItems = extractIndividualInventorySlots(inventory)
    return inventoryItems
    } catch (error) {
    throw new Error(error)
    }
  }
  
  export function extractIndividualInventorySlots(inventory) {
    let slotsContent = {}
    for (let slot of inventory) {
      slotsContent[slot.code] = slot.quantity
    }
    return slotsContent
  }
  