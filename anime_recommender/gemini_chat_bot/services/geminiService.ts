
import { GoogleGenAI, Chat } from "@google/genai";
import type { GenerateContentResponse } from "@google/genai";

const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  throw new Error("API_KEY environment variable not set");
}

const ai = new GoogleGenAI({ apiKey: API_KEY });

const chat: Chat = ai.chats.create({
  model: 'gemini-2.5-flash',
  config: {
    tools: [{ googleSearch: {} }],
  },
});

export const streamChatResponse = async (message: string) => {
  return chat.sendMessageStream({ message });
};

export const extractSources = (response: GenerateContentResponse): { uri: string; title: string }[] => {
  const groundingChunks = response.candidates?.[0]?.groundingMetadata?.groundingChunks;
  if (!groundingChunks) {
    return [];
  }

  return groundingChunks
    .map((chunk) => {
      if ('web' in chunk && chunk.web && chunk.web.uri && chunk.web.title) {
        return {
          uri: chunk.web.uri,
          title: chunk.web.title,
        };
      }
      return null;
    })
    .filter((source): source is { uri: string; title: string } => source !== null);
};
