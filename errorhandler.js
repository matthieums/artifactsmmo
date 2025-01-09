import { errorMessages } from "./errorcodes.js";

export function handleErrorCode(errorCode) {
    const message = errorMessages[errorCode] || errorMessages.default;
    console.error(`Error ${errorCode}: ${message}`);
    throw new Error(message);
}