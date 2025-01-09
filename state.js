
import { getCurrentPosition, getCurrentLevels } from "./api.js";
import { compareObjects, extractLevelsFrom } from "./utils.js";

export let CURRENT_POSITION = null;
export let CURRENT_LEVELS = {};
export const locations = {
    // Monsters
    "chicken": [0, 1],
    "cow": [0, 2],
    "green_slime": [0, -1],

    // Resources
    "copper": [2, 0],
    "ash_tree": [-1, 0],
    "sunflower": [2, 2],

    // Crafting stations
    "weapon": [2, 1],
    "food": [1, 1],
    "forge": [1, 5],
    "armor": [3, 1],

    "bank": [4, 1],

    "santa_claus": [1, 19]
}


export function atTargetLocation(target) {
    return (JSON.stringify(CURRENT_POSITION) === JSON.stringify(target));
}

export async function setCurrentPosition() {
    const position = await getCurrentPosition();
    updatePosition(position);
}

export function updatePosition(position) {
    const [x, y] = position;
    CURRENT_POSITION = [x, y];
}

export async function setCurrentLevels() {
    const currentLevels = await getCurrentLevels();
    const stats = extractLevelsFrom(currentLevels)
    const keys = Object.keys(stats)

    for (let key of keys) {
        CURRENT_LEVELS[key] = stats[key]
    }
    
}

export function UpdateLevels(stats) {
    if (stats && Array.isArray(stats)) {
        for (let stat of stats) {
            CURRENT_LEVELS[stat] += 1
            console.log(CURRENT_LEVELS[stat])
        }
    }
}

// Now I should create a dictionary that contains all levellable stats
// Each levellable should be compared to its previous value.
// If a difference is found: Add the level difference to the script end log
// Maybe the script end log should be a big object containing lots of values 
// Depending on the action
export async function checkForAnyLevelUp(levelsToCheck) {
    const keys = compareObjects(CURRENT_LEVELS !== levelsToCheck)
    const levelsGained = {}
    if (keys) {
        for (let key of keys) {
            console.log(`${key} levelled up to ${levelsToCheck[key]}`)
            levelsGained[key] = levelsToCheck[key]
        }
        UpdateLevels(keys)
        return levelsGained
    } else {
        return false;
    }
}

