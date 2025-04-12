
import { handleErrorCode } from "./errorhandling/errorhandler.js";
import { updatePosition, atTargetLocation, checkForAnyLevelUp } from "./state.js";
import { waitForCooldown, displayCombatLog, extractLevelsFrom, 
setupBankRequest} from "./utils.js";
import { locations } from "./locations.js";
import { rl } from "./main.js";
import urlBuilder, { character } from "./urlBuilder.js";
import requestOptionsBuilder from "./requestOptionsBuilder.js";
import getNecessaryResourcesToCraft from "./crafting.js";

let INFINITE_TRIGGER = false;

// MOVE TO LOCATION
export async function moveTo(target) {
  const location = locations[target]

  if (atTargetLocation(location)) {
    console.log('Already at destination')
    return;
  }

  const [x, y] = location;
  const body = {x, y};
  const url = urlBuilder.getMoveActionUrl();
  const requestOptions = requestOptionsBuilder.buildPostRequestOptions(body);

  try {
    const response = await fetch(url, requestOptions);

    if (!response.ok) {
      handleErrorCode(response.status);
    }

  const { data: { cooldown: { total_seconds } } } = await response.json();

  console.log(`Succesfully moved to (${x}, ${y})`);
  updatePosition(location)

  await waitForCooldown(total_seconds, character)
  
  } catch (error) {
    throw new Error(error)
  }
}


// CRAFT ITEMS
export async function craft(station, code, quantity) {
  try {
    await getNecessaryResourcesToCraft(code, quantity);
    await moveTo(station);
  } catch (error) {
    throw new Error(error.message)
  }

  try {
    const body = { code, quantity }
    const requestOptions = requestOptionsBuilder.buildPostRequestOptions(body)
    const url = urlBuilder.getCraftActionUrl()

    const response = await fetch(url, requestOptions);

    if (!response.ok) {
        handleErrorCode(response.status);
    }

    const { data: { cooldown: { total_seconds } } } = await response.json();
    console.log(`Crafted: ${quantity} ${code}`);
    await waitForCooldown(total_seconds);

  } catch(error) {
    console.error(error.message);
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

  let INFINITE_TRIGGER = true;
  while(INFINITE_TRIGGER) {
    try {
      const requestOptions = requestOptionsBuilder.buildPostRequestOptions();
      const url = urlBuilder.getFightActionUrl();
      const response = await fetch(url, requestOptions);

      if (!response.ok) {
        handleErrorCode(response.status);
      }

      response = await response.json();

      parseFightLoot(response.data)

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

      const { data: { cooldown: { total_seconds } } } = await response.json();

      displayCombatLog(monster, feedback);

      await waitForCooldown(total_seconds)

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
    requestOptio
    ns = switchToPostRequest(requestOptions);
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

// Deposit
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

// Withdraw
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


// EQUIP
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


export function exit() {
  console.log('Exiting...');
  rl.close();
  }