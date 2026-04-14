If you are expecting a single object instead of a list (array), you need to change two things: the **type definition** in the Hook and the **initial value**.

When you use `[]`, you are telling React to expect a collection. When you want just one, you are telling React to expect a single "shape."

### The Code Changes

Here is how you would rewrite the `useState` hook:

```typescript
// 1. Initializing with 'null' (Common if data is fetched later)
const [progress, setProgress] = useState<SkillProfile | null>(null);

// OR 

// 2. Initializing with a default object
const [progress, setProgress] = useState<SkillProfile>({
  user_id: 0,
  topic_id: 0,
  skill_score: 0,
  confidence_score: 0,
  id: 0
});
```

---

### Key Differences to Watch Out For

| Feature | List (Array) | Single Object |
| :--- | :--- | :--- |
| **Type Syntax** | `SkillProfile[]` | `SkillProfile` |
| **Initial Value** | `[]` (Empty array) | `null` or `{ ...defaults }` |
| **Accessing Data** | `progress.map(...)` | `progress.user_id` |
| **Check if empty** | `progress.length > 0` | `progress !== null` |

---

### Why use `null`?
In React, it’s very common to start a single-object state as `null`. This is because, at the exact millisecond the page loads, you don't have the user's data yet. 

If you use `null`, you have to use **Optional Chaining** in your HTML (JSX) to prevent the app from crashing while it waits for data:

```tsx
// This says: "Only try to show user_id if progress actually exists"
<p>User ID: {progress?.user_id}</p>
```



### A Quick "Gotcha"
If your state is a single object and you accidentally try to do `progress.map()`, your app will throw an error saying **"progress.map is not a function."** Mapping only works on arrays!

**Would you like me to show you how to handle the loading state properly so your page doesn't look "broken" while the object is being fetched?**