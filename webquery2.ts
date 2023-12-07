import { MongoClient } from 'mongodb';

// Replace the following with your MongoDB connection string.
const uri = 'mongodb://localhost:27017';
const dbName = 'numbers';
const collectionName = 'num';

async function main(target) {
    const client = new MongoClient(uri);
  
    console.time('ExecutionTime'); // Start the timer

    try {
        // Connect to the MongoDB cluster
        await client.connect();
        const database = client.db(dbName);
        const collection = database.collection(collectionName);

        // Get the total count of documents in the collection
        const totalCount = await collection.countDocuments();

        // Find the closest number to the target number
        let closest = null;
        let smallestDiff = Number.MAX_SAFE_INTEGER;

        // Iterate through documents to find the closest number
        let low = 0;
        let high = totalCount - 1;  // totalCount instead of cursor.count()

        while (low <= high) {
            let mid = Math.floor((low + high) / 2);

            // Retrieve the document at the mid position
            const cursor = collection.find().skip(mid).limit(1);
            const doc = await cursor.next();

            const diff = Math.abs(target - doc.num);
            if (diff < smallestDiff) {
                smallestDiff = diff;
                closest = doc;
            }
            if (target < doc.num) {
                high = mid - 1;
            }
            else {
                low = mid + 1;
            }
        };

        if (closest) {
            console.log(`The closest number to ${target} is ${closest.num} with _id: ${closest._id}`);
        } else {
            console.log('No numbers found in the database.');
        }

    } finally {
        // Close the connection to the MongoDB cluster
        await client.close();
        console.timeEnd('ExecutionTime'); // End the timer and log the result
    }
}

main(59000).catch(console.error);
