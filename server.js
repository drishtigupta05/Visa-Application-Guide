const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const OpenAI = require("openai");
const visaData = require("./visaData.json");

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// Create OpenAI client
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    // If using a scaledown / proxy provider,
    // add baseURL here if required:
    baseURL: "https://api.scaledown.xyz"
});

app.post("/chat", async (req, res) => {
    const userMessage = req.body.message;

    try {

        // Build context from your visa JSON
        const context = JSON.stringify(visaData);

        const completion = await openai.chat.completions.create({
            model: "gpt-4o-mini",
            messages: [
                {
                    role: "system",
                    content: "You are a visa application assistant. Use the provided visa data to answer clearly and concisely."
                },
                {
                    role: "user",
                    content: `Visa Data: ${context}\n\nUser Question: ${userMessage}`
                }
            ],
            temperature: 0.3
        });

        const reply = completion.choices[0].message.content;

        res.json({ reply });

    } catch (error) {
        console.error(error);
        res.status(500).json({ reply: "AI error occurred." });
    }
});

app.listen(5000, () => console.log("Server running on port 5000"));
