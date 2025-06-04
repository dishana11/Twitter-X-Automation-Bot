#!/usr/bin/env python3
"""
Twitter Automation Bot - Main Entry Point
A comprehensive Twitter bot with scheduled posting, auto-replies, hashtag monitoring, and sentiment analysis.
"""

import os
import sys
import time
import signal
import argparse
from threading import Thread, Event
from bot.twitter_bot import TwitterBot
from utils.logger import setup_logger
from config.settings import load_config

# Global event for graceful shutdown
shutdown_event = Event()
logger = setup_logger('main')

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info("Received shutdown signal. Stopping bot...")
    shutdown_event.set()

def main():
    """Main function to run the Twitter automation bot"""
    parser = argparse.ArgumentParser(description='Twitter Automation Bot')
    parser.add_argument('--config', '-c', default='config/config.json', 
                       help='Path to configuration file')
    parser.add_argument('--mode', '-m', choices=['full', 'monitor', 'schedule', 'reply'], 
                       default='full', help='Bot operation mode')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Load configuration
        config = load_config(args.config)
        if not config:
            logger.error("Failed to load configuration. Exiting.")
            sys.exit(1)
        
        # Initialize the Twitter bot
        bot = TwitterBot(config, shutdown_event)
        
        logger.info(f"Starting Twitter Bot in {args.mode} mode...")
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Start the bot based on mode
        if args.mode == 'full':
            bot.start_full_automation()
        elif args.mode == 'monitor':
            bot.start_hashtag_monitoring()
        elif args.mode == 'schedule':
            bot.start_scheduled_posting()
        elif args.mode == 'reply':
            bot.start_auto_replies()
        
        # Keep the main thread alive
        while not shutdown_event.is_set():
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Bot shutdown complete.")

if __name__ == "__main__":
    main()
