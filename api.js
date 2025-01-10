
import { handleErrorCode } from "./errorhandler.js";
import { locations, updatePosition, atTargetLocation, checkForAnyLevelUp } from "./state.js";
import { waitForCooldown, displayCombatLog, switchToGetRequest,
  switchToPostRequest, extractLevelsFrom, handleScriptInterruption,
setupBankRequest} from "./utils.js";

let INFINITE_TRIGGER = false;

const token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6Im1hcnRlbnMubWF0dGhpZXVAaG90bWFpbC5jb20iLCJwYXNzd29yZF9jaGFuZ2VkIjoiIn0.ARDWMe5_tUvMPvrrNR_-tuSAOcr1EWOPruhYFj3u_FY";
const server = "https://api.artifactsmmo.com";
export const character = "Arthurus"
// Considering to use other characters? 
// I will need to create a "busy" trigger, and find a way to locate a character
// So I can send the closer one to the location I'm needing someone at

var myHeaders = new Headers();
myHeaders.append("Accept", "application/json");
myHeaders.append("Content-Type", "application/json");
myHeaders.append("Authorization", `Bearer ${token}`);

var requestOptions = {
  method: 'POST',
  headers: myHeaders,
  redirect: 'follow'
}


// MOVE TO LOCATION
export async function moveTo(target) {
  const location = locations[target]
  if (atTargetLocation(location)) {
    return
  }
  console.log(`Attempting to move to ${location}`)
  requestOptions = switchToPostRequest(requestOptions)
  const [x, y] = location

  try {
    requestOptions['body'] =     
    JSON.stringify({
      x: x,
      y: y 
    });

    const response = await fetch(`${server}/my/${character}/action/move`, requestOptions);

    if (!response.ok) {
      handleErrorCode(response.status)
  }
  
  const feedback = await response.json()
  const cooldownInSeconds = feedback.data.cooldown.total_seconds
  console.log(`Moved to (${x}, ${y})`);
  updatePosition(location)
  await waitForCooldown(cooldownInSeconds)
  } catch(error) {
    throw new Error(error)
  }
}

async function getItemRecipe(item) {
  const url = `${server}/items/${item}`
  requestOptions = switchToGetRequest(requestOptions)
  
  try {
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



async function getNecessaryResourcesToCraft(item, amount) {
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


async function characterHasEnoughMaterialFor(items, amount) {
  const inventory = await getCharacterInventory();

  // Check if I have enough material for the amount
  // of items I want to craft


//   "inventory": [
//     "slot": 0,
//     "code": "string",
//     "quantity": 0
// ]

  for (let item of items) {
    let code = item.code
    const requiredQuantity = item.quantity * amount;
    if (!inventory[code] || inventory[code] < requiredQuantity) {
      return false;
    }
  }
  return true;
}


async function getCharacterInventory() {
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

function extractIndividualInventorySlots(inventory) {
  let slotsContent = {}
  for (let slot of inventory) {
    slotsContent[slot.code] = slot.quantity
  }
  return slotsContent
}


// CRAFT ITEMS
export async function craft(station, code, quantity) {
  try {
    // await getNecessaryResourcesToCraft(code, quantity)
    await moveTo(station);
  } catch (error) {
    throw new Error(error.message)
  }

  // Get necessary resources => Modify withdraw function to handle inventory
  requestOptions = switchToPostRequest(requestOptions);
  requestOptions['body'] = JSON.stringify({
      code: code,
      quantity: quantity
  });
  INFINITE_TRIGGER = true;
  while (INFINITE_TRIGGER){
  try {
    const response = await fetch(`${server}/my/${character}/action/crafting`, requestOptions);
    if (!response.ok) {
        handleErrorCode(response.status);
    }
    const feedback = await response.json();
    const cooldownInSeconds = feedback.data.cooldown.total_seconds;
    console.log(`Crafted: ${quantity} of ${code}`);
    await waitForCooldown(cooldownInSeconds);
  } catch(error) {
    console.error(error.message);
  }
}
}




// FIGHT
export async function fight(monster) {

  await moveTo(monster);

  let LootGained = {}
  let levelsGained = {}
  let xp = 0;
  const scriptData = {
    loot: LootGained,
    levels: levelsGained,
    xp: xp
  }

  handleScriptInterruption(scriptData);

  requestOptions = switchToPostRequest(requestOptions);

  INFINITE_TRIGGER = true;
  while(INFINITE_TRIGGER) {
    try {
      const response = await fetch(`${server}/my/${character}/action/fight`, requestOptions);
      if (!response.ok) {
        handleErrorCode(response.status);
      }

      const feedback = await response.json()

      const fightData = feedback.data.fight
      const { xp, gold, drops } = fightData
      





      scriptData.loot['gold'] = gold
      drops.forEach(drop => {
        if (!scriptData.loot[drop.code]) {
          scriptData.loot[drop.code] = 0;
        }
        scriptData.loot[drop.code] += drop.quantity;
      });
      
      scriptData.xp += parseInt(xp);

      const character_data = feedback.data.character
      const levels = extractLevelsFrom(character_data)
      const levelUps = checkForAnyLevelUp(levels)

      if (levelUps) {
        Object.entries(levelUps).forEach(([key, value]) => {
          console.log(`Level up: ${key}: ${value} \n`)
          scriptData.levels[key] = value;
        })}

      const cooldownInSeconds = feedback.data.cooldown.total_seconds
      
      displayCombatLog(monster, feedback)
      await waitForCooldown(cooldownInSeconds)

      if (feedback.data.character.hp < 20) {
        await rest();
      }
    } catch(error) {
        console.log('Error in fight function:', error);
        throw error;
    }
  } 
}

  

// GATHER
export async function gather(location) {
  
  await moveTo(location)

  let LootGained = {}
  let levelsGained = {}
  let xp = 0
  const scriptData = {
    loot: LootGained,
    levels: levelsGained,
    xp: xp
  }

  handleScriptInterruption(scriptData);
  INFINITE_TRIGGER = true;

  while (INFINITE_TRIGGER) {
    requestOptions = switchToPostRequest(requestOptions)
    const response = await fetch(`${server}/my/${character}/action/gathering`, requestOptions);
    if (!response.ok) {
      handleErrorCode(response.status);
    }
    const data = await response.json()
    const details = data.data.details
    const cooldown = data.data.cooldown
    const character_data = data.data.character
    
    scriptData.xp += parseInt(details.xp);

    const levels = extractLevelsFrom(character_data)
    const levelUps = checkForAnyLevelUp(levels)
    
    if (levelUps) {
      Object.entries(levelUps).forEach(([key, value]) => {
        console.log(`Level up: ${key}: ${value} \n`)
        scriptData.levels[key] = value;
      })
    }

    const cooldownInSeconds = cooldown.total_seconds

    const items = details.items
    items.forEach(item => {
      if (!scriptData.loot[item.code]) {
        scriptData.loot[item.code] = 0;
      }
      scriptData.loot[item.code] += item.quantity;
    });

    console.log(`\nGathered:`)
    items.forEach(item => console.log(item.quantity, item.code));
    await waitForCooldown(cooldownInSeconds);
  }
}

  export async function rest() {
    requestOptions = switchToPostRequest(requestOptions);
    const response = await fetch(`${server}/my/${character}/action/rest`, requestOptions);
    const data = await response.json()
    const cooldownInSeconds = data.data.cooldown.total_seconds
    const hp = data.data.character.hp
    const hpRestored = data.data.hp_restored
    const maxHp = data.data.character.max_hp
    await waitForCooldown(cooldownInSeconds)
    console.log(`Rested. Restored ${hpRestored} hp. `)
    console.log(`HP: ${hp}/${maxHp}`)
    console.log(`Resting...`)
  }




// BANK ACTIONS
export async function deposit(code, quantity) {
  
  await moveTo('bank');
  requestOptions = setupBankRequest(requestOptions, code, quantity)

  try {
    const response = await fetch(`${server}/my/${character}/action/bank/deposit`, requestOptions)
    if (!response.ok) {
      handleErrorCode(response.status);
    }
    console.log(`Succesfully deposited ${quantity} ${code}`)
  } catch (error) {
    throw new Error(error.message)
  }
}

export async function withdraw(code, quantity) {
  
  await moveTo('bank');
  requestOptions = setupBankRequest(requestOptions, code, quantity)

  try {
    const response = await fetch(`${server}/my/${character}/action/bank/withdraw`, requestOptions)
    if (!response.ok) {
      handleErrorCode(response.status);
    }
    const data = await response.json()
    console.log(`Succesfully withdrew ${quantity} ${code}`)
    await waitForCooldown(data.data.cooldown.total_seconds)
  } catch (error) {
    throw new Error(error.message)
  }
}


export async function getCurrentPosition() {
  requestOptions = switchToGetRequest(requestOptions);

  try {
    const url = `${server}/my/characters/`;
    const response = await fetch(url, requestOptions);

    if(!response.ok) {
        handleErrorCode(response.status)
    }

    const data = await response.json()
    const x = data.data[0]['x']
    const y = data.data[0]['y']
    return [x, y]

  } catch (error) {
    console.error('Error fetching position:', error);
    throw error;
  }
}

export async function equip(code, slot, quantity) {
  const url = `${server}/my/${character}/action/equip`

  requestOptions = switchToPostRequest(requestOptions);
  requestOptions['body'] = JSON.stringify({
    'code': code,
    'slot': slot,
    'quantity': quantity
  })

  try {
    const response = fetch(url, requestOptions);
    if (!response.ok) {
      handleErrorCode(response.status)
    }
    console.log(`Succesfully equipped ${code} to ${slot}`)
  } catch (error) {
    throw error
  }
}


  // Returns a list of key, values containing a stat and its current level
  export async function getCurrentLevels() {
    requestOptions = switchToGetRequest(requestOptions);
    try {
        const url = `${server}/my/characters/`;
        const response = await fetch(url, requestOptions);
    
        if(!response.ok) {
            handleErrorCode(response.status)
        }
    
        const data = await response.json()
        const character_data = data.data[0]
        const levels = extractLevelsFrom(character_data)
        return levels
    
      } catch (error) {
        console.error('Error fetching position:', error);
        throw error;
      }
}
