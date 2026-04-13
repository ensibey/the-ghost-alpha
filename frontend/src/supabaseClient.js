import { createClient } from '@supabase/supabase-js'

// Vite exposes env variables prefixed with VITE_
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://mock-url.supabase.co'
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY || 'mock-key'

export const supabase = createClient(supabaseUrl, supabaseKey)
