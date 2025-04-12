
export async function waitForCooldown(cooldown, character) {
    const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

    let remainingCooldown =  cooldown
    console.log(`\nCharacter in cooldown:\n${remainingCooldown} seconds left...`)

    const interval = setInterval(() => {
      console.log(`${remainingCooldown} seconds left...`)
    }, 5000)

    while (remainingCooldown > 0) {
      await delay(1000);
      remainingCooldown--;
    }
    console.log(`${character} is idle...`)
    clearInterval(interval);
    return
  }



// This function will allow comparison of two dictionaries
// That have the same keys
// It should return a list of the keys that sustained
// changes
export function compareObjects(obj1, obj2) {
  const keys = Object.keys(obj1)
  const keysWithDifferentValues = []

  for (let key of keys) {
    if (obj1[key] !== obj2[key]) {
        keysWithDifferentValues.push(key)
    }
  }
  return keysWithDifferentValues
}

  // Function to get the stat levels from api response
export function extractLevelsFrom(data) {
  const levels = {
    level : data.level,
    mining_level : data.mining_level,
    woodcutting_level : data.woodcutting_level,
    fishing_level : data.fishing_level,
    weaponcrafting_level : data.weaponcrafting_level,
    gearcrafting_level : data.gearcrafting_level,
    jewelrycrafting_level : data.jewelrycrafting_level,
    cooking_level : data.cooking_level,
    alchemy_level : data.alchemy_level
  }
  return levels
}




  /**
 * Handles scriptinterruption and logs changes.
 */
export function handleScriptInterruption(bundle) {
  // Interrupt on ctrl + c
    process.on('SIGINT', () => {
      console.log('\n **** Script interrupted ****');
      logLootAndXp(bundle)
      process.exit(0);
    });
  
    // Interrupt on error
    process.on('uncaughtException', (error) => {
      console.error('Uncaught exception:', error);
      console.log('Script terminated due to an error.');
      logLootAndXp(bundle)
      process.exit(1);
    });
}

export function setupBankRequest(requestOptions, code, quantity) {
  requestOptions = switchToPostRequest(requestOptions)
  requestOptions['body'] = ''
  requestOptions['body'] = JSON.stringify({
    "code": code,
    "quantity": quantity
  })
  return requestOptions
}