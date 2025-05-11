import React from "react";

interface AddTaskProps {
  characterName: string;
    taskName: string;
    iterations: number
  kwargs: {
    resource?: string;
    target?: string;
    location?: string;
    quantity?: number;
  };
}

export function AddTask({ characterName, iterations, taskName, kwargs }: AddTaskProps) {
    return (
        <button onClick={onclickHandler}>
            {`Add  ${iterations}x ${taskName} ${Object.values(kwargs)}`}
        </button>
    )

    async function onclickHandler() {
        const taskPayload = {
            iterations: 1,
            character_name: characterName,
            task_name: taskName,
            args: [],
            kwargs: kwargs
        };

        try {
            const response = await fetch("http://127.0.0.1:8000/task", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(taskPayload)
            });

            const result = await response.json();
            console.log(result);
        } catch (error) {
            console.error("Error submitting task:", error);
        }

    }
}