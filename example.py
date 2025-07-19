from pycdp.googlecdp import ChromeManager
from pycdp.keys import Key, HotKey
from time import sleep

def main():
    chrome = ChromeManager(
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",  
        r"C:\Users\vovab\AppData\Local\Google\Chrome\User Data\Default",  
        False,
    )

    chrome.start_session(
        "--window-size=1280,800",
        "--no-first-run",
        "--no-default-browser-check",
        "--new-window"
    )
    chrome.init_ws_connection()

    chrome.navigate("https://www.google.com")
    sleep(2)
    chrome.scroll(300)
    
    elem = chrome.execute_script("""
        let elem = document.getElementsByClassName('gLFyf')[0];
                                 
        elem.value = 'Chrome DevTools Protocol';
        elem.dispatchEvent(new Event('input', { bubbles: true }));
        elem.focus();
    """)
    chrome.send_key(Key.Return)
    print(elem)
    

if __name__ == "__main__":
    main()