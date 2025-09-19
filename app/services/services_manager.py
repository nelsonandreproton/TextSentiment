import asyncio
import subprocess
import logging
import aiohttp
import platform
import time
import pymongo
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class ServicesManager:
    def __init__(self, ollama_url: str = "http://localhost:11434", mongodb_url: str = "mongodb://localhost:27017"):
        self.ollama_url = ollama_url
        self.mongodb_url = mongodb_url
        self.ollama_process: Optional[subprocess.Popen] = None
        self.mongodb_process: Optional[subprocess.Popen] = None
        self.system = platform.system().lower()

    async def is_ollama_running(self) -> bool:
        """Check if Ollama service is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    return response.status == 200
        except Exception:
            return False

    async def is_mongodb_running(self) -> bool:
        """Check if MongoDB service is running."""
        try:
            client = AsyncIOMotorClient(self.mongodb_url, serverSelectionTimeoutMS=3000)
            await client.admin.command('ping')
            client.close()
            return True
        except Exception:
            return False

    async def start_mongodb_service(self) -> bool:
        """Start MongoDB service if not running."""
        try:
            # Check if already running
            if await self.is_mongodb_running():
                logger.info("MongoDB service is already running")
                return True

            logger.info("Starting MongoDB service...")

            if self.system == "windows":
                # Try different Windows MongoDB start methods
                start_commands = [
                    ["net", "start", "MongoDB"],  # Windows service
                    ["sc", "start", "MongoDB"],   # Service control
                    ["mongod", "--dbpath", "C:\\data\\db"],  # Direct start with default path
                ]

                for cmd in start_commands:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            logger.info(f"MongoDB started with command: {' '.join(cmd)}")
                            break
                    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                        logger.debug(f"Command {cmd} failed: {e}")
                        continue
                else:
                    logger.warning("Could not start MongoDB using standard Windows methods")

            elif self.system == "linux":
                # Try Linux systemd and other methods
                start_commands = [
                    ["sudo", "systemctl", "start", "mongod"],
                    ["sudo", "service", "mongod", "start"],
                    ["mongod", "--fork", "--logpath", "/var/log/mongodb/mongod.log"],
                ]

                for cmd in start_commands:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            logger.info(f"MongoDB started with command: {' '.join(cmd)}")
                            break
                    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                        logger.debug(f"Command {cmd} failed: {e}")
                        continue
                else:
                    logger.warning("Could not start MongoDB using standard Linux methods")

            elif self.system == "darwin":  # macOS
                # Try macOS methods
                start_commands = [
                    ["brew", "services", "start", "mongodb-community"],
                    ["sudo", "launchctl", "load", "/Library/LaunchDaemons/org.mongodb.mongod.plist"],
                    ["mongod", "--config", "/usr/local/etc/mongod.conf", "--fork"],
                ]

                for cmd in start_commands:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            logger.info(f"MongoDB started with command: {' '.join(cmd)}")
                            break
                    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                        logger.debug(f"Command {cmd} failed: {e}")
                        continue
                else:
                    logger.warning("Could not start MongoDB using standard macOS methods")

            # Wait and check if MongoDB is now running
            for i in range(10):  # Wait up to 10 seconds
                await asyncio.sleep(1)
                if await self.is_mongodb_running():
                    logger.info("MongoDB service started successfully")
                    return True

            logger.error("MongoDB service failed to start")
            return False

        except Exception as e:
            logger.error(f"Failed to start MongoDB service: {e}")
            return False

    async def start_ollama_service(self) -> bool:
        """Start Ollama service if not running."""
        try:
            # Check if already running
            if await self.is_ollama_running():
                logger.info("Ollama service is already running")
                return True

            logger.info("Starting Ollama service...")

            try:
                if self.system == "windows":
                    self.ollama_process = subprocess.Popen(
                        ["ollama", "serve"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    self.ollama_process = subprocess.Popen(
                        ["ollama", "serve"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
            except FileNotFoundError:
                logger.error("Ollama not found in PATH. Please install Ollama or add it to PATH.")
                return False

            # Wait for the service to start
            for i in range(10):  # Wait up to 10 seconds
                await asyncio.sleep(1)
                if await self.is_ollama_running():
                    logger.info("Ollama service started successfully")
                    return True

            logger.error("Ollama service failed to start within 10 seconds")
            return False

        except Exception as e:
            logger.error(f"Failed to start Ollama service: {e}")
            return False

    async def ensure_ollama_model(self, model_name: str = "nomic-embed-text") -> bool:
        """Ensure the required Ollama model is available."""
        try:
            if not await self.is_ollama_running():
                logger.error("Ollama service is not running")
                return False

            # Check if model is available
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags") as response:
                    if response.status != 200:
                        return False

                    data = await response.json()
                    models = [model.get("name", "") for model in data.get("models", [])]

                    # Check if our model is in the list
                    model_available = any(model_name in model for model in models)

                    if model_available:
                        logger.info(f"Model {model_name} is available")
                        return True
                    else:
                        logger.warning(f"Model {model_name} not found. Please run: ollama pull {model_name}")
                        return False

        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False

    async def initialize_all_services(self) -> Dict[str, bool]:
        """Initialize all required services."""
        results = {
            "mongodb": False,
            "ollama": False,
            "ollama_model": False
        }

        try:
            # Start MongoDB
            logger.info("🗄️ Checking MongoDB service...")
            results["mongodb"] = await self.start_mongodb_service()

            if results["mongodb"]:
                logger.info("✅ MongoDB service is ready")
            else:
                logger.error("❌ MongoDB service failed to start")

            # Start Ollama
            logger.info("🤖 Checking Ollama service...")
            results["ollama"] = await self.start_ollama_service()

            if results["ollama"]:
                logger.info("✅ Ollama service is ready")

                # Check Ollama model
                logger.info("📦 Checking Ollama model...")
                results["ollama_model"] = await self.ensure_ollama_model()

                if results["ollama_model"]:
                    logger.info("✅ Ollama model is ready")
                else:
                    logger.warning("⚠️ Ollama model not available")
            else:
                logger.error("❌ Ollama service failed to start")

            return results

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            return results

    def stop_all_services(self):
        """Stop all services that we started."""
        logger.info("🔄 Stopping all services...")

        try:
            # Stop Ollama if we started it
            if self.ollama_process:
                logger.info("🛑 Stopping Ollama service...")
                self.ollama_process.terminate()
                try:
                    self.ollama_process.wait(timeout=5)
                    logger.info("✅ Ollama service stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️ Ollama didn't stop gracefully, forcing...")
                    self.ollama_process.kill()
                    logger.info("✅ Ollama service force stopped")
                finally:
                    self.ollama_process = None
            else:
                logger.info("ℹ️ No Ollama process to stop (externally managed)")

            # Note: MongoDB is typically a system service, so we don't stop it
            logger.info("ℹ️ MongoDB service left running (system service)")

            logger.info("✅ All services cleanup completed")

        except Exception as e:
            logger.error(f"❌ Error stopping services: {e}")

    def get_service_status(self) -> Dict[str, str]:
        """Get current status of all services."""
        return {
            "system": self.system,
            "ollama_url": self.ollama_url,
            "mongodb_url": self.mongodb_url,
            "ollama_process_running": self.ollama_process is not None and self.ollama_process.poll() is None,
        }

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop_all_services()