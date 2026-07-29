import { getAvailableGates } from "./api.js";

document.addEventListener("DOMContentLoaded", async () => {

    try {

        const gates = await getAvailableGates();

        console.log(gates);

    } catch (err) {

        console.error(err);

    }

});
