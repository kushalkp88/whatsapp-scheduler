/**
 * send_message.cjs
 *
 * Sends a WhatsApp message (and optional image) to a contact using @open-wa/wa-automate.
 * Usage: node send_message.cjs <phone> <message> [image]
 */

const wa = require('@open-wa/wa-automate');
const fs = require('fs');
const path = require('path');

// Parse command-line arguments
const args = process.argv.slice(2);
if (args.length < 2) {
    console.error('Usage: node send_message.cjs <phone> <message> [image]');
    process.exit(1);
}
const [phone, message, imagePath] = args;

// Ensure phone number is in WhatsApp format (remove + and non-digits)
const cleanPhone = phone.replace(/[^\d]/g, '') + '@c.us';

// wa-automate config for Mac (use Chrome, headless for automation)
wa.create({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
    sessionId: 'whatsapp-scheduler',
    multiDevice: true,
    qrTimeout: 0,
    authTimeout: 60,
    blockCrashLogs: true,
    disableSpins: true,
    logConsole: false,
    popup: false // <--- Disable the popup server!
}).then(async client => {
    try {
    // Send text message
    await client.sendText(cleanPhone, message);
    console.log(`Message sent to ${phone}`);

    // If imagePath provided, send image
    if (imagePath && imagePath.trim() !== '') {
        let resolvedImage = imagePath;
        if (!/^https?:\/\//.test(imagePath)) {
            resolvedImage = path.resolve(imagePath);
            if (!fs.existsSync(resolvedImage)) {
                throw new Error(`Image file not found: ${resolvedImage}`);
            }
        }
        await client.sendImage(cleanPhone, resolvedImage, path.basename(resolvedImage), message);
        console.log(`Image sent to ${phone}`);
    }

    // Wait to ensure message delivery before closing (e.g., 15 seconds)
    console.log('Waiting 15 seconds to ensure message delivery...');
    await new Promise(resolve => setTimeout(resolve, 15000));

    await client.kill();
    process.exit(0);
} catch (err) {
    // Log the error with details and exit with failure code
    console.error('Error during WhatsApp automation:', err.message || err);
    await client.kill();
    process.exit(1);
}

}).catch(err => {
    console.error('Error initializing wa-automate:', err);
    process.exit(1);
});
