import type { APIRoute } from 'astro';
import source from '../../../examples/send-more-money.cpp?raw';

export const GET: APIRoute = () => new Response(source, {
  headers: {
    'Content-Type': 'text/x-c++src; charset=utf-8',
    'Content-Disposition': 'attachment; filename="send-more-money.cpp"',
  },
});
