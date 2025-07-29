#!/bin/bash

# Vercel Environment Variables Setup Script
echo "Setting up Vercel environment variables..."

VERCEL_TOKEN="t6arPbXGjmc2TCmCjvOFWJvk"
PROJECT_ID="prj_eEQBr1Cr6KxGdLgAbNpVD4CrwEYD"  # Get this from Vercel dashboard

# Function to add environment variable
add_env_var() {
    local name=$1
    local value=$2
    local target=${3:-production}
    
    echo "Adding $name..."
    vercel env add "$name" "$target" --token "$VERCEL_TOKEN" < <(echo "$value")
}

# Firebase Environment Variables
add_env_var "NEXT_PUBLIC_FIREBASE_API_KEY" "AIzaSyB0g7f_313m1pvVDA7hTQthldNTkjvrgF8"
add_env_var "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN" "priority-appraisal-ai-tool.firebaseapp.com"
add_env_var "NEXT_PUBLIC_FIREBASE_PROJECT_ID" "priority-appraisal-ai-tool"
add_env_var "NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET" "priority-appraisal-ai-tool.appspot.com"
add_env_var "NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID" "155312316711"
add_env_var "NEXT_PUBLIC_FIREBASE_APP_ID" "1:155312316711:web:5728ed9367b192cc968902"
add_env_var "FIREBASE_CLIENT_EMAIL" "firebase-adminsdk-fbsvc@priority-appraisal-ai-tool.iam.gserviceaccount.com"

# Private key needs special handling due to newlines
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCr6S74V+ELDZsK
ZiJ6HkFL/Rb8n3u2xpvAVfI6GKNUraqtFDrbj6h2TTksWq3t0U2cCTu7JqM+JFL3
ortL4zGmXHwhAwa0yclDinnGEN/kjUkSl8fsdUwGoNs4r4SwT+nvcrxZDNeoaZyG
MO8W5I6QFLF0UQyFPjmgIVQiZ+/GYkPToSoDpssWUC+b2m+TZMHzqp41P9o4vhCb
gYGLlQcyyIcwGOyuNY9K3hFwsw4la4sap8bZH1nLlVWw8bqjY+L2/x7+dMZH1Ymn
eOOxixkiO0ACV2EO95C3RVrmls+R0TwP6c+WhhXgGvsZ2jWs1lfBQV2w1oP3ria1
AviVkR7tAgMBAAECggEAE/6F+6pfk+UxisRq7ssatcIqQe2GpQZ1J6nssfxwRVwB
hX8x1/GIcAyhQVsL7voF+HJLzoOQPvJYl/wG+VeOTGwQn9egmGGpFUBDfi7eQNB8
luYCVv/O0i0z8g7anusHKVYDOVQ4t5oOSL6OQEUK87pZvU6Okedf1ROrRmknm79c
LLScW4549rnZmzh+/nF8OIfDjZCi2xNOwGyPX2KRhJib3t8TAnRSyXoynNPK+P4U
ssJ24IhQGMnEAItDk+fJP4BDsp8gTlrTGpL9oIYJJm+JfTkRBi+6d7FrE3ldJnm4
XviFjmzknA1kh8NbM76U92CYy4wigiIniUErgtS7nQKBgQDvYSQVw/HioxN+i8WO
Si9zV/kTr1F79z16qTTl4QkCaVnYYCp9t3Yrbt2ohmjZ8kMofBVyhjPt1DtgiEq6
oDBJHJcVj4bJNh6RO4xcYZxayJiY3jUihPwDzocrmn09MMcqxG4792Z7TQ6mcOIT
YfDB0/1xL/fySPB3jt8eQk1vHwKBgQC32NHV63JBwjESM3GUfTdSgOpJYOy7EtL6
EA6GxyFU+8iy4eEMS1PAZ8YaM3tBtVsWXP76wzwBfyombfbC9aSn55aaIn6zJHwR
gfyH6SN+tk7tPf+TY9C9klTKOxofLMjcX9yNzUb53pqz2OwIe/vUN9cADnfilMHQ
qi+PRdVMcwKBgQDkeuqvX6RLdu3Pdmds5cAertRNhqQW16i1oDWeSMmJpLadwUQt
VGQVFq+4//mqNQMG7FCoTBHaqhy2icASG32a+w/2A1VaTi6k3pqdPom3WQnVtxou
RZIprAH2i3GIaztexbiVwhDuFWGrWclfSLc8ujOIyok1l4r2AsdRoWU5bwKBgQCy
swfTnRXkITO9c0+Ve9jIUxJn3NR+Sh/UfMMB8pDNoCdG6RPs9VMlFDmUwjGufu9Y
32/gouCyu75muEBA5K/1nL/gdmMdEfuesPCb0ttzkRVKuRaxVzZQ7emI4MXVQ5zB
yFQDaWLyAZPx+IoE/S6c6uIK5gVVsi5p+uJbqw9XTQKBgETuAML6RTfDjFS6RTSu
7gpln7IHX1h6SKNxi8G6F7zLKXhYHxUQiHoLqZgt+GgUx2TM2U7rD1DkSDQHlj9z
uowMkxhG4Oe4VYN4SW1Dscc82ojuSNmPotsDjCAxkEsCPi3UsPGWViD3+lcZXWeD
+wCINPDit0AUlzHrNr54TdBH
-----END PRIVATE KEY-----"

add_env_var "FIREBASE_PRIVATE_KEY" "$FIREBASE_PRIVATE_KEY"

echo "Environment variables setup complete!"
echo "Now redeploy your application for changes to take effect."