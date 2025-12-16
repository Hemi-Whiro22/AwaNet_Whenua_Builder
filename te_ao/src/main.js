import axios from 'axios';

// Function to fetch project state from the server
async function fetchProjectState() {
    try {
        // Make a GET request to the server to fetch the project state
        const response = await axios.get('http://localhost:10000/state/public');
        const state = response.data;
        console.log('Project state loaded:', state);

        // Store the fetched state in local storage
        localStorage.setItem('projectState', JSON.stringify(state));

        // Configure the API base URL using the fetched state
        if (state.urls && state.urls.render) {
            axios.defaults.baseURL = state.urls.render;
        }
    } catch (error) {
        // Log any error that occurs during the fetch operation
        console.error('Failed to fetch project state:', error);
    }
}

// Fetch project state when the application boots up
fetchProjectState();