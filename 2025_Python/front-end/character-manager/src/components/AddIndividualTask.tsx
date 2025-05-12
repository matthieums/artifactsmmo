import React, { useState } from "react";
import { apiFetch } from "../utils";

interface AddTaskProps {
  characterName: string;
    taskName: string;
  kwargs: {
    resource?: string;
    location?: string;
    quantity?: number;
  };
}

export function AddTask({ characterName, taskName, kwargs }: AddTaskProps) {
    const [iterations, setIterations] = useState<number>(1)
    
    return (
        <div>
            <input 
                type="number"
                value={iterations}
                onChange={(e) => setIterations(Number(e.target.value))}
             />
            <button onClick={onclickHandler}>
                {`Add ${taskName} ${Object.values(kwargs)}`}
            </button>
        </div>
    )

    async function onclickHandler() {
        const taskPayload = {
            iterations: iterations,
            character_name: characterName,
            task_name: taskName,
            args: [],
            kwargs: kwargs
        };

        try {
            await apiFetch("/task", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(taskPayload)
            });
        } catch (error) {
            console.error("Error submitting task:", error);
        }
    }
}