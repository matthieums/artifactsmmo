import React, { useState } from "react";
import { apiFetch } from "../utils";

interface AddGroupTaskProps {
    taskName: string;
  kwargs?: {
    resource?: string;
    location?: string;
    quantity?: number;
  };
}

export function AddGroupTask({taskName, kwargs }: AddGroupTaskProps) {
    const [iterations, setIterations] = useState<number>(1)
    const [quantity, setQuantity] = useState<number>(0)
    
    let quantityInput = null
    if (taskName === "gather") {
        quantityInput = 
            <input 
                type="number"
                value={quantity}
                onChange={(e) => setQuantity(Number(e.target.value))}
                placeholder="How much?"
            />
    }

    return (
        <div>
            <input 
                type="number"
                value={iterations}
                onChange={(e) => setIterations(Number(e.target.value))}
             />
            <button onClick={onclickHandler}>
                {`Add ${taskName} ${Object.values(kwargs?? {})}`}
            </button>
            {quantityInput}
        </div>
    )

    async function onclickHandler() {
        const finalKwargs = {
            ...(kwargs || {}),
            ...(taskName === "gather" && quantity ? { quantity } : {})
        }
        const taskPayload = {
            iterations: iterations,
            task_name: taskName,
            args: [],
            kwargs: finalKwargs
        };

        try {
            await apiFetch("/group_task", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(taskPayload)
            });
        } catch (error) {
            console.error("Error submitting task:", error);
        }
    }
}