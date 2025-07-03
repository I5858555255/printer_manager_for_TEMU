// ==UserScript==
// @name         一键打印发货单 (Kuaijingmaihuo Batch Print)
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Adds a button to print SKUs and quantities from the kuajingmaihuo shipping list page.
// @author       You
// @match        https://seller.kuajingmaihuo.com/main/order-manager/shipping-list
// @grant        GM_xmlhttpRequest
// @grant        GM_addStyle
// @grant        GM_getValue
// @grant        GM_setValue
// ==/UserScript==

(function() {
    'use strict';

    // --- Configuration ---
    // The user will need to configure this URL if their local printer software API endpoint is different.
    const PRINTER_API_URL = 'http://localhost:8080/print'; // Example: Replace with actual local printer API

    // --- Main Function ---
    function main() {
        console.log('Tampermonkey script loaded for kuajingmaihuo.');
        addPrintButton();
    }

    // --- Helper Functions ---

    function addPrintButton() {
        const button = document.createElement('button');
        button.textContent = '一键打印';
        button.id = 'oneClickPrintButton';
        button.addEventListener('click', handleOneClickPrint);

        // Apply some basic styling
        GM_addStyle(`
            #oneClickPrintButton {
                position: fixed;
                top: 10px;
                right: 10px;
                z-index: 9999;
                padding: 10px 15px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }
            #oneClickPrintButton:hover {
                background-color: #0056b3;
            }
        `);

        // Try to append to a main content area, otherwise fallback to body
        // The user might need to adjust this selector based on the live page structure
        let targetContainer = document.querySelector('#container') || document.querySelector('#app') || document.body;
        if (targetContainer) {
            targetContainer.appendChild(button);
            console.log('Print button added.');
        } else {
            console.error('Could not find a suitable container to add the print button.');
        }
    }

    async function handleOneClickPrint() {
        console.log('一键打印 button clicked.');

        // --- Placeholder Selectors - USER NEEDS TO UPDATE THESE ---
        const orderRowSelector = '.order-item'; // Example: Adjust to actual class for order rows
        const packageDetailsButtonSelector = '.package-details-button'; // Example: Button to show details
        const skuSelector = '.sku-id'; // Example: Element containing SKU
        const quantitySelector = '.shipped-quantity'; // Example: Element containing shipped quantity
        const nextOrderTriggerSelector = '.next-order-button'; // Example: If orders are loaded one by one

        // --- Data Collection ---
        let allOrderData = [];
        let errorOrders = [];

        // Get all order rows. This might need to be adjusted if orders are loaded dynamically.
        const orderRows = document.querySelectorAll(orderRowSelector);

        if (orderRows.length === 0) {
            alert('No order rows found. Please check the selector: ' + orderRowSelector);
            return;
        }

        console.log(`Found ${orderRows.length} order rows.`);

        for (let i = 0; i < orderRows.length; i++) {
            const orderRow = orderRows[i];
            console.log(`Processing order row ${i + 1}...`);

            try {
                // --- Step 1: Click "Package Details" (Hypothetical) ---
                // This part is highly dependent on page structure.
                // If SKU/quantity are directly visible, this can be removed.
                // const detailsButton = orderRow.querySelector(packageDetailsButtonSelector);
                // if (detailsButton) {
                //     console.log('Clicking package details button...');
                //     detailsButton.click();
                //     // Wait for details to load (e.g., using a timeout or MutationObserver)
                //     // This is a simple placeholder; a more robust solution might be needed.
                //     await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
                // } else {
                //     console.log('Package details button not found for this order, assuming data is visible.');
                // }

                // --- Step 2: Extract SKU and Quantity ---
                const skuElement = orderRow.querySelector(skuSelector);
                const quantityElement = orderRow.querySelector(quantitySelector);

                let sku = null;
                let quantity = null;

                if (skuElement) {
                    sku = skuElement.textContent.trim();
                } else {
                    console.error(`SKU element not found in order row ${i + 1} using selector: ${skuSelector}`);
                    errorOrders.push({ orderIndex: i + 1, error: 'SKU not found' });
                    continue; // Skip to next order if SKU is missing
                }

                if (quantityElement) {
                    // Assuming quantity is a number, try to parse it.
                    // The text might be like "x 5" or "5件", so extraction logic might be needed.
                    // For now, a simple textContent trim. User might need to refine.
                    const quantityText = quantityElement.textContent.trim();
                    const quantityMatch = quantityText.match(/\d+/); // Try to extract numbers
                    if (quantityMatch) {
                        quantity = parseInt(quantityMatch[0], 10);
                    }
                }

                if (sku && quantity !== null) {
                    console.log(`Order ${i + 1}: SKU = ${sku}, Quantity = ${quantity}`);
                    allOrderData.push({ sku, quantity, orderIndex: i + 1 });
                } else if (sku && quantity === null) {
                    console.error(`Quantity element found but could not parse quantity in order row ${i + 1} using selector: ${quantitySelector}. Text was: "${quantityElement ? quantityElement.textContent : 'N/A'}"`);
                    errorOrders.push({ orderIndex: i + 1, error: 'Quantity not found or unparsable', sku: sku });
                } else {
                    // SKU was not found, error already logged.
                }

            } catch (error) {
                console.error(`Error processing order row ${i + 1}:`, error);
                errorOrders.push({ orderIndex: i + 1, error: error.message });
            }
        }

        console.log('--- Collected Order Data ---');
        console.log(allOrderData);

        if (errorOrders.length > 0) {
            console.warn('--- Orders with Errors ---');
            console.warn(errorOrders);
            alert(`Finished processing, but ${errorOrders.length} order(s) had errors. Check console for details.`);
        }

        if (allOrderData.length === 0 && orderRows.length > 0) {
            alert('Could not extract data from any order. Please check console and selectors.');
            return;
        }

        if (allOrderData.length === 0 && orderRows.length === 0) {
             // Already alerted above
            return;
        }


        // --- Step 3: Printing Action (Placeholder for now) ---
        if (allOrderData.length > 0) {
            // --- Step 3: Printing Action ---
            console.log("--- Sending data to printer API ---");
            for (const order of allOrderData) {
                await callPrinterAPI(order.sku, order.quantity, order.orderIndex);
                // Optional: Add a small delay between API calls if needed by the printer software
                // await new Promise(resolve => setTimeout(resolve, 200)); // 200ms delay
            }
            alert('All processed orders sent to printer API. Check console for individual statuses.');
        }
    }

    async function callPrinterAPI(sku, quantity, orderIndex) {
        console.log(`Sending to printer: SKU ${sku}, Quantity ${quantity} for order index ${orderIndex}`);

        // The structure of the data sent (JSON payload, query parameters)
        // will depend on the local printer software's API requirements.
        // This is an example assuming a JSON POST request.
        const payload = JSON.stringify({
            sku: sku,
            quantity: quantity,
            // You can add more data if your printer software needs it
            // timestamp: new Date().toISOString()
        });

        return new Promise((resolve, reject) => {
            GM_xmlhttpRequest({
                method: "POST",
                url: PRINTER_API_URL,
                data: payload,
                headers: {
                    "Content-Type": "application/json"
                },
                onload: function(response) {
                    if (response.status >= 200 && response.status < 300) {
                        console.log(`Successfully sent to printer (Order Index ${orderIndex}): ${response.responseText}`);
                        resolve(response);
                    } else {
                        console.error(`Printer API error (Order Index ${orderIndex}): ${response.status} - ${response.responseText}`);
                        alert(`Error sending order index ${orderIndex} to printer. Status: ${response.status}`);
                        reject(response);
                    }
                },
                onerror: function(response) {
                    console.error(`Printer API request failed (Order Index ${orderIndex}):`, response);
                    alert(`Failed to send order index ${orderIndex} to printer. Is the printer software running and API URL correct?`);
                    reject(response);
                }
            });
        });
    }

    // --- Entry Point ---
    // Ensure the page is fully loaded before running the main script logic,
    // especially for dynamic pages.
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', main);
    } else {
        main();
    }

})();
