
import requestOptionsBuilder from "./requestOptionsBuilder.js";
import urlBuilder from "./urlBuilder.js";
import { compareObjects, extractLevelsFrom } from "./utils.js";


export let CURRENT_POSITION = null;
export let CURRENT_LEVELS = {};

export async function fetchState() {
 await setCurrentPosition();
 await setCurrentLevels();
 return;
}

export function atTargetLocation(target) {
    console.log(CURRENT_POSITION, target)
    return (CURRENT_POSITION == target);
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

 // Returns a list of key, values containing a stat and its current level
  export async function getCurrentLevels() {
    const requestOptions = requestOptionsBuilder.buildGetRequestOptions();
    const url = urlBuilder.getCharactersUrl();

    try {
        const response = await fetch(url, requestOptions);

        if(!response.ok) {
            handleErrorCode(response.status);
            return;
        }

        const data = await response.json();
        const character_data = data.data[0];

        const levels = extractLevelsFrom(character_data);

        return levels

    } catch (error) {
        console.error('Error fetching position:', error);
        throw error;
    }
}

export async function getCurrentPosition() {
  try {
    const requestOptions = requestOptionsBuilder.buildGetRequestOptions();
    const url = urlBuilder.getCharactersUrl();

    const response = await fetch(url, requestOptions);

    if(!response.ok) {
        handleErrorCode(response.status)
    }

    const { data } = await response.json();
    const { x, y } = data[0];

    return [x, y];

  } catch (error) {
    console.error('Error fetching position:', error);
    throw error;
  }
}
