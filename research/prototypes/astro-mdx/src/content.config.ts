import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'zod';

const chapters = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/chapters' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    chapter: z.number().int().positive(),
    order: z.number().int().nonnegative(),
  }),
});

export const collections = { chapters };
