
import { handleErrorCode } from "./errorhandling/errorhandler.js";
import { updatePosition, atTargetLocation, checkForAnyLevelUp } from "./state.js";
import { waitForCooldown, displayCombatLog, extractLevelsFrom, 
handleScriptInterruption, setupBankRequest} from "./utils.js";
import { getCharacterInventory } from "./inventory.js";
import { locations } from "./locations.js";
import { rl } from "./main.js";
import urlBuilder from "./urlBuilder.js";
import requestOptionsBuilder from "./requestOptionsBuilder.js";

const character = "Arthurus"

let INFINITE_TRIGGER = false;

// MOVE TO LOCATION
export async function moveTo(target) {

  const location = locations[target]

  if (atTargetLocation(location)) {
    return;
  }

  const [x, y] = location;
  const body = {x, y};
  const url = urlBuilder.getMoveActionUrl();
  console.log(url)
  const requestOptions = requestOptionsBuilder.buildPostRequestOptions(body);
  console.log(requestOptions)
  try {
    const response = await fetch(url, requestOptions);
    if (!response.ok) {
      handleErrorCode(response.status)
  }
  const feedback = await response.json()
  const cooldownInSeconds = feedback.data.cooldown.total_seconds
  console.log(`Succesfully moved to (${x}, ${y})`);
  updatePosition(location)
  await waitForCooldown(cooldownInSeconds, character)
  } catch(error) {
    throw new Error(error)
  }
}



// CRAFT ITEMS
export async function craft(station, code, quantity) {
  try {
    await getNecessaryResourcesToCraft(code, quantity)
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
    const levelUps = await checkForAnyLevelUp(levels)
    
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

  for (let item of items) {
    let code = item.code
    const requiredQuantity = item.quantity * amount;
    if (!inventory[code] || inventory[code] < requiredQuantity) {
      return false;
    }
  }
  return true;
}

export function exit() {
  console.log('Exiting...');
  rl.close();
  }