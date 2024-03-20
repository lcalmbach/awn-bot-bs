mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"lcalmbach@gmail.com\"\n\
" > ~/.streamlit/credentials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\

[theme]\n\
primaryColor = '#070707'\n\
backgroundColor = '#fcfcfc'\n\
secondaryBackgroundColor = '#e3e3e3'\n\
textColor = '#070707'\n\

" > ~/.streamlit/config.toml