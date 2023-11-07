import { MongoClient } from 'mongodb';

// Replace the following with your MongoDB connection string.
const uri = 'mongodb://localhost:27017';
const dbName = 'numbers';
const collectionName = 'num';


async function main(target: number) {
  const client = new MongoClient(uri);

  try {
    // Connect to the MongoDB cluster
    await client.connect();
    const database = client.db(dbName);
    const collection = database.collection(collectionName);

        // Find the closest number to the target number
        // We sort by the absolute difference and get the first document
        // let closest = await collection.find({ num: { $gte: target } }).sort({ num: 1 }).limit(1).toArray();
        // // If no number greater than or equal to the target is found, check for the closest lesser number
        // if (!closest.length) {
        //     closest = await collection.find().sort({ num: { $lt: target } }).limit(1).toArray();
        // }

        // if (closest.length) {
        //     console.log(`The closest number to ${target} is ${closest[0].num}`);
        // } else {
        //     console.log('No number found in the database.');
        // }

        let closest = null;
        let smallestDiff = Number.MAX_SAFE_INTEGER;

        // Cursor to iterate over all documents in the collection
        const cursor = collection.find();

        // Loop through all documents to find the closest number
        for await (const doc of cursor) {
            const diff = Math.abs(target - doc.num);
            if (diff < smallestDiff) {
                smallestDiff = diff;
                closest = doc;
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
    }
}
main(500).catch(console.error);

