
const BASE_URL = "https://api.artifactsmmo.com";
const character = "Arthurus"
// Considering to use other characters? 
// I will need to create a "busy" trigger, and find a way to locate a character
// So I can send the closer one to the location I'm needing someone at

function getMoveActionUrl() {
    return `${BASE_URL}/my/${character}/action/move`
}



export default {
    getMoveActionUrl
  };
