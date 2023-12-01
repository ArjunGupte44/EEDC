"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
var __asyncValues = (this && this.__asyncValues) || function (o) {
    if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
    var m = o[Symbol.asyncIterator], i;
    return m ? m.call(o) : (o = typeof __values === "function" ? __values(o) : o[Symbol.iterator](), i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i);
    function verb(n) { i[n] = o[n] && function (v) { return new Promise(function (resolve, reject) { v = o[n](v), settle(resolve, reject, v.done, v.value); }); }; }
    function settle(resolve, reject, d, v) { Promise.resolve(v).then(function(v) { resolve({ value: v, done: d }); }, reject); }
};
Object.defineProperty(exports, "__esModule", { value: true });
var mongodb_1 = require("mongodb");
// Replace the following with your MongoDB connection string.
var uri = 'mongodb://localhost:27017';
var dbName = 'numbers';
var collectionName = 'num';
function main(target) {
    var _a, e_1, _b, _c;
    return __awaiter(this, void 0, void 0, function () {
        var client, database, collection, closest, smallestDiff, cursor, _d, cursor_1, cursor_1_1, doc, diff, e_1_1;
        return __generator(this, function (_e) {
            switch (_e.label) {
                case 0:
                    client = new mongodb_1.MongoClient(uri);
                    console.time('ExecutionTime'); // Start the timer
                    _e.label = 1;
                case 1:
                    _e.trys.push([1, , 15, 17]);
                    // Connect to the MongoDB cluster
                    return [4 /*yield*/, client.connect()];
                case 2:
                    // Connect to the MongoDB cluster
                    _e.sent();
                    database = client.db(dbName);
                    collection = database.collection(collectionName);
                    closest = null;
                    smallestDiff = Number.MAX_SAFE_INTEGER;
                    cursor = collection.find();
                    _e.label = 3;
                case 3:
                    _e.trys.push([3, 8, 9, 14]);
                    _d = true, cursor_1 = __asyncValues(cursor);
                    _e.label = 4;
                case 4: return [4 /*yield*/, cursor_1.next()];
                case 5:
                    if (!(cursor_1_1 = _e.sent(), _a = cursor_1_1.done, !_a)) return [3 /*break*/, 7];
                    _c = cursor_1_1.value;
                    _d = false;
                    doc = _c;
                    diff = Math.abs(target - doc.num);
                    if (diff < smallestDiff) {
                        smallestDiff = diff;
                        closest = doc;
                    }
                    _e.label = 6;
                case 6:
                    _d = true;
                    return [3 /*break*/, 4];
                case 7: return [3 /*break*/, 14];
                case 8:
                    e_1_1 = _e.sent();
                    e_1 = { error: e_1_1 };
                    return [3 /*break*/, 14];
                case 9:
                    _e.trys.push([9, , 12, 13]);
                    if (!(!_d && !_a && (_b = cursor_1.return))) return [3 /*break*/, 11];
                    return [4 /*yield*/, _b.call(cursor_1)];
                case 10:
                    _e.sent();
                    _e.label = 11;
                case 11: return [3 /*break*/, 13];
                case 12:
                    if (e_1) throw e_1.error;
                    return [7 /*endfinally*/];
                case 13: return [7 /*endfinally*/];
                case 14:
                    ;
                    if (closest) {
                        console.log("The closest number to ".concat(target, " is ").concat(closest.num, " with _id: ").concat(closest._id));
                    }
                    else {
                        console.log('No numbers found in the database.');
                    }
                    return [3 /*break*/, 17];
                case 15: 
                // Close the connection to the MongoDB cluster
                return [4 /*yield*/, client.close()];
                case 16:
                    // Close the connection to the MongoDB cluster
                    _e.sent();
                    console.timeEnd('ExecutionTime'); // End the timer and log the result
                    return [7 /*endfinally*/];
                case 17: return [2 /*return*/];
            }
        });
    });
}
main(390).catch(console.error);
