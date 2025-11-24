import asyncio
import base64
import asyncssh
import sys

# Usage: python test_connection.py <host> <password>

async def run_test(host, password):
    print(f"Connecting to {host}...")
    try:
        async with asyncssh.connect(host, username='root', password=password, known_hosts=None) as conn:
            print("Connected!")
            
            cmd = (
                "luna-send -n 1 -f luna://com.webos.service.capture/executeOneShot "
                "'{\"path\":\"/tmp/webos_cam.png\", \"method\":\"DISPLAY\", \"format\":\"PNG\", \"width\":960, \"height\":540}' "
                "&& base64 /tmp/webos_cam.png "
                "&& rm /tmp/webos_cam.png"
            )
            
            print("Executing capture command...")
            result = await conn.run(cmd, check=True)
            
            print("Command finished.")
            stdout = result.stdout.strip()
            print(f"Received {len(stdout)} bytes of stdout.")
            
            if not stdout:
                print("Error: No output received.")
                return

            try:
                image_data = base64.b64decode(stdout)
                print(f"Successfully decoded {len(image_data)} bytes of image data.")
                with open("test_capture.png", "wb") as f:
                    f.write(image_data)
                print("Saved to test_capture.png")
            except Exception as e:
                print(f"Error decoding base64: {e}")

    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_connection.py <host> <password>")
        sys.exit(1)
    
    asyncio.run(run_test(sys.argv[1], sys.argv[2]))
