// API Configuration
const API_URL = 'http://localhost:3000/api';

// Data Storage (for local cache)
let medications = [];
let reminders = [];
let vitals = [];
let appointments = [];

// Audio context for sound alerts
let audioContext;
let hasPlayedSound = new Set(); // Track which reminders have played sound

// Initialize app on load
document.addEventListener('DOMContentLoaded', function() {
    loadData();
    checkReminders();
    requestNotificationPermission();
    initAudioContext();
    // Check reminders every minute
    setInterval(checkReminders, 60000);
});

// Initialize Audio Context
function initAudioContext() {
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    } catch (e) {
        console.log('Web Audio API not supported');
    }
}

// Play notification sound
function playNotificationSound(type = 'reminder') {
    if (!audioContext) {
        initAudioContext();
    }
    
    // Resume audio context if suspended (required by browsers)
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
    
    try {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        // Different sounds for different alerts
        if (type === 'urgent') {
            // Urgent alert: rapid beeping
            oscillator.frequency.value = 800;
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            
            oscillator.start(audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
            oscillator.stop(audioContext.currentTime + 0.1);
            
            setTimeout(() => {
                const osc2 = audioContext.createOscillator();
                const gain2 = audioContext.createGain();
                osc2.connect(gain2);
                gain2.connect(audioContext.destination);
                osc2.frequency.value = 800;
                gain2.gain.setValueAtTime(0.3, audioContext.currentTime);
                osc2.start(audioContext.currentTime);
                gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
                osc2.stop(audioContext.currentTime + 0.1);
            }, 200);
        } else {
            // Standard reminder: pleasant chime
            oscillator.type = 'sine';
            oscillator.frequency.setValueAtTime(523.25, audioContext.currentTime); // C5
            oscillator.frequency.setValueAtTime(659.25, audioContext.currentTime + 0.1); // E5
            oscillator.frequency.setValueAtTime(783.99, audioContext.currentTime + 0.2); // G5
            
            gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.5);
        }
    } catch (error) {
        console.error('Error playing sound:', error);
        // Fallback: try to play a beep using the default system sound
        try {
            const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBi2Izffilz0OFFy36+62YBADOJfW8sJwKQQjeMrz2ZBGDBY4lt3ux2QRATuZ2u+tXhMIM5nV76ZMGAg7mtfwslwV');
            audio.play().catch(e => console.log('Fallback sound failed:', e));
        } catch (e) {
            console.log('All sound playback methods failed');
        }
    }
}

// Load all data from API
async function loadData() {
    try {
        await Promise.all([
            loadMedications(),
            loadReminders(),
            loadVitals(),
            loadAppointments()
        ]);
        updateStatistics();
    } catch (error) {
        console.error('Error loading data:', error);
        showToast('Failed to load data. Please check your connection.');
    }
}

// Show toast notification
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Update statistics
function updateStatistics() {
    document.getElementById('totalMeds').textContent = medications.length;
    
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    const todayReminders = reminders.filter(r => {
        const reminderDate = new Date(r.date_time);
        reminderDate.setHours(0, 0, 0, 0);
        return reminderDate.getTime() === today.getTime();
    });
    document.getElementById('todayReminders').textContent = todayReminders.length;
    
    const upcomingAppointments = appointments.filter(a => new Date(a.date_time) >= new Date());
    document.getElementById('upcomingAppointments').textContent = upcomingAppointments.length;
    
    document.getElementById('vitalRecords').textContent = vitals.length;
}

// ==================== MEDICATION FUNCTIONS ====================

async function loadMedications() {
    try {
        const response = await fetch(`${API_URL}/medications`);
        if (!response.ok) throw new Error('Failed to fetch medications');
        medications = await response.json();
        renderMedications();
    } catch (error) {
        console.error('Error loading medications:', error);
        showToast('Failed to load medications');
    }
}

async function addMedication() {
    const name = document.getElementById('medName').value;
    const dosage = document.getElementById('medDosage').value;
    const frequency = document.getElementById('medFrequency').value;
    const time = document.getElementById('medTime').value;
    
    if (!name || !dosage || !time) {
        showToast('Please fill in all medication fields');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/medications`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, dosage, frequency, time })
        });
        
        if (!response.ok) throw new Error('Failed to add medication');
        
        document.getElementById('medName').value = '';
        document.getElementById('medDosage').value = '';
        document.getElementById('medTime').value = '';
        
        await loadMedications();
        updateStatistics();
        showToast('Medication added successfully!');
    } catch (error) {
        console.error('Error adding medication:', error);
        showToast('Failed to add medication');
    }
}

function renderMedications() {
    const list = document.getElementById('medicationList');
    
    if (medications.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">💊</div>
                <div class="empty-state-text">No medications added yet</div>
            </div>
        `;
        return;
    }
    
    list.innerHTML = medications.map(med => `
        <div class="list-item">
            <div class="list-item-header">
                <span class="list-item-title">${med.name}</span>
                ${med.taken ? '<span class="badge badge-success">Taken</span>' : '<span class="badge badge-warning">Pending</span>'}
            </div>
            <div class="list-item-content">
                <p><strong>Dosage:</strong> ${med.dosage}</p>
                <p><strong>Frequency:</strong> ${med.frequency}</p>
                <p><strong>Time:</strong> ${med.time}</p>
            </div>
            <div class="list-item-actions">
                ${!med.taken ? `<button class="btn btn-success" onclick="markTaken(${med.id})">Mark as Taken</button>` : ''}
                <button class="btn btn-danger" onclick="deleteMedication(${med.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

async function markTaken(id) {
    try {
        const response = await fetch(`${API_URL}/medications/${id}/taken`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ taken: true })
        });
        
        if (!response.ok) throw new Error('Failed to update medication');
        
        await loadMedications();
        showToast('Medication marked as taken!');
    } catch (error) {
        console.error('Error updating medication:', error);
        showToast('Failed to update medication');
    }
}

async function deleteMedication(id) {
    if (!confirm('Are you sure you want to delete this medication?')) return;
    
    try {
        const response = await fetch(`${API_URL}/medications/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete medication');
        
        await loadMedications();
        updateStatistics();
        showToast('Medication deleted');
    } catch (error) {
        console.error('Error deleting medication:', error);
        showToast('Failed to delete medication');
    }
}

// ==================== REMINDER FUNCTIONS ====================

async function loadReminders() {
    try {
        const response = await fetch(`${API_URL}/reminders`);
        if (!response.ok) throw new Error('Failed to fetch reminders');
        reminders = await response.json();
        renderReminders();
    } catch (error) {
        console.error('Error loading reminders:', error);
        showToast('Failed to load reminders');
    }
}

async function addReminder() {
    const title = document.getElementById('reminderTitle').value;
    const dateTime = document.getElementById('reminderDateTime').value;
    const notes = document.getElementById('reminderNotes').value;
    
    if (!title || !dateTime) {
        showToast('Please fill in title and date/time');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/reminders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                title, 
                date_time: dateTime, 
                notes 
            })
        });
        
        if (!response.ok) throw new Error('Failed to add reminder');
        
        document.getElementById('reminderTitle').value = '';
        document.getElementById('reminderDateTime').value = '';
        document.getElementById('reminderNotes').value = '';
        
        await loadReminders();
        updateStatistics();
        showToast('Reminder set successfully!');
    } catch (error) {
        console.error('Error adding reminder:', error);
        showToast('Failed to add reminder');
    }
}

function renderReminders() {
    const list = document.getElementById('reminderList');
    
    if (reminders.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⏰</div>
                <div class="empty-state-text">No reminders set</div>
            </div>
        `;
        return;
    }
    
    list.innerHTML = reminders.map(rem => {
        const reminderDate = new Date(rem.date_time);
        const now = new Date();
        const isPast = reminderDate < now;
        
        return `
            <div class="list-item">
                <div class="list-item-header">
                    <span class="list-item-title">${rem.title}</span>
                    ${isPast ? '<span class="badge badge-danger">Past</span>' : '<span class="badge badge-success">Upcoming</span>'}
                </div>
                <div class="list-item-content">
                    <p><strong>Date & Time:</strong> ${formatDateTime(rem.date_time)}</p>
                    ${rem.notes ? `<p><strong>Notes:</strong> ${rem.notes}</p>` : ''}
                </div>
                <div class="list-item-actions">
                    <button class="btn btn-danger" onclick="deleteReminder(${rem.id})">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

async function deleteReminder(id) {
    if (!confirm('Are you sure you want to delete this reminder?')) return;
    
    try {
        const response = await fetch(`${API_URL}/reminders/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete reminder');
        
        // Remove from hasPlayedSound set
        hasPlayedSound.delete(id);
        
        await loadReminders();
        updateStatistics();
        showToast('Reminder deleted');
    } catch (error) {
        console.error('Error deleting reminder:', error);
        showToast('Failed to delete reminder');
    }
}

function checkReminders() {
    const now = new Date();
    
    reminders.forEach(reminder => {
        const reminderTime = new Date(reminder.date_time);
        const timeDiff = reminderTime - now;
        
        // Alert 5 minutes before (300000 ms = 5 minutes)
        if (timeDiff > 0 && timeDiff <= 300000 && !reminder.notified && !hasPlayedSound.has(`${reminder.id}-5min`)) {
            // Play sound alert
            playNotificationSound('reminder');
            
            // Show browser notification
            sendNotification(reminder.title, `Reminder in 5 minutes: ${reminder.title}`);
            
            // Show toast
            showToast(`⏰ Reminder: ${reminder.title} in 5 minutes!`);
            
            // Mark as notified on server
            fetch(`${API_URL}/reminders/${reminder.id}/notify`, {
                method: 'PUT'
            }).catch(err => console.error('Failed to mark reminder as notified:', err));
            
            // Track that we've played sound for this reminder
            hasPlayedSound.add(`${reminder.id}-5min`);
            reminder.notified = true;
        }
        
        // Alert when reminder time arrives
        else if (timeDiff > -60000 && timeDiff <= 0 && !hasPlayedSound.has(`${reminder.id}-now`)) {
            // Play urgent sound alert
            playNotificationSound('urgent');
            
            sendNotification(reminder.title, `It's time: ${reminder.title}!`);
            showToast(`🔔 Time for: ${reminder.title}!`);
            
            fetch(`${API_URL}/reminders/${reminder.id}/notify`, {
                method: 'PUT'
            }).catch(err => console.error('Failed to mark reminder as notified:', err));
            
            // Track that we've played sound for this reminder
            hasPlayedSound.add(`${reminder.id}-now`);
        }
    });
}

// Browser Notification System
function sendNotification(title, body) {
    if (!("Notification" in window)) {
        console.log("This browser does not support desktop notifications");
        return;
    }
    
    if (Notification.permission === "granted") {
        createNotification(title, body);
    }
    else if (Notification.permission !== "denied") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                createNotification(title, body);
            }
        });
    }
}

function createNotification(title, body) {
    const notification = new Notification(title, {
        body: body,
        icon: '🏥',
        badge: '🏥',
        tag: 'medical-reminder',
        requireInteraction: true,
        vibrate: [200, 100, 200],
    });
    
    notification.onclick = function() {
        window.focus();
        notification.close();
    };
}

function requestNotificationPermission() {
    if ("Notification" in window && Notification.permission === "default") {
        showToast("Please allow notifications to receive reminders!");
        setTimeout(() => {
            Notification.requestPermission().then(permission => {
                if (permission === "granted") {
                    showToast("Notifications enabled! You'll receive reminders.");
                } else {
                    showToast("Notifications disabled. You won't receive alerts.");
                }
            });
        }, 2000);
    }
}

// ==================== VITAL SIGNS FUNCTIONS ====================

async function loadVitals() {
    try {
        const response = await fetch(`${API_URL}/vitals`);
        if (!response.ok) throw new Error('Failed to fetch vitals');
        vitals = await response.json();
        renderVitals();
    } catch (error) {
        console.error('Error loading vitals:', error);
        showToast('Failed to load vital signs');
    }
}

async function addVitalSigns() {
    const bloodPressure = document.getElementById('bloodPressure').value;
    const heartRate = document.getElementById('heartRate').value;
    const temperature = document.getElementById('temperature').value;
    const bloodSugar = document.getElementById('bloodSugar').value;
    
    if (!bloodPressure && !heartRate && !temperature && !bloodSugar) {
        showToast('Please enter at least one vital sign');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/vitals`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                blood_pressure: bloodPressure || null,
                heart_rate: heartRate || null,
                temperature: temperature || null,
                blood_sugar: bloodSugar || null
            })
        });
        
        if (!response.ok) throw new Error('Failed to add vital signs');
        
        document.getElementById('bloodPressure').value = '';
        document.getElementById('heartRate').value = '';
        document.getElementById('temperature').value = '';
        document.getElementById('bloodSugar').value = '';
        
        await loadVitals();
        updateStatistics();
        showToast('Vital signs recorded!');
    } catch (error) {
        console.error('Error adding vital signs:', error);
        showToast('Failed to record vital signs');
    }
}

function renderVitals() {
    const list = document.getElementById('vitalsList');
    
    if (vitals.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">❤️</div>
                <div class="empty-state-text">No vital signs recorded</div>
            </div>
        `;
        return;
    }
    
    list.innerHTML = vitals.map(vital => `
        <div class="list-item">
            <div class="list-item-header">
                <span class="list-item-title">Vital Signs</span>
                <span class="badge badge-success">${formatDate(vital.recorded_date)}</span>
            </div>
            <div class="list-item-content">
                ${vital.blood_pressure ? `<p><strong>Blood Pressure:</strong> ${vital.blood_pressure} mmHg</p>` : ''}
                ${vital.heart_rate ? `<p><strong>Heart Rate:</strong> ${vital.heart_rate} bpm</p>` : ''}
                ${vital.temperature ? `<p><strong>Temperature:</strong> ${vital.temperature}°F</p>` : ''}
                ${vital.blood_sugar ? `<p><strong>Blood Sugar:</strong> ${vital.blood_sugar} mg/dL</p>` : ''}
            </div>
            <div class="list-item-actions">
                <button class="btn btn-danger" onclick="deleteVital(${vital.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

async function deleteVital(id) {
    if (!confirm('Are you sure you want to delete this vital record?')) return;
    
    try {
        const response = await fetch(`${API_URL}/vitals/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete vital record');
        
        await loadVitals();
        updateStatistics();
        showToast('Vital record deleted');
    } catch (error) {
        console.error('Error deleting vital record:', error);
        showToast('Failed to delete vital record');
    }
}

// ==================== APPOINTMENT FUNCTIONS ====================

async function loadAppointments() {
    try {
        const response = await fetch(`${API_URL}/appointments`);
        if (!response.ok) throw new Error('Failed to fetch appointments');
        appointments = await response.json();
        renderAppointments();
    } catch (error) {
        console.error('Error loading appointments:', error);
        showToast('Failed to load appointments');
    }
}

async function addAppointment() {
    const doctor = document.getElementById('appointmentDoctor').value;
    const type = document.getElementById('appointmentType').value;
    const dateTime = document.getElementById('appointmentDateTime').value;
    const location = document.getElementById('appointmentLocation').value;
    
    if (!doctor || !dateTime) {
        showToast('Please fill in doctor name and date/time');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/appointments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                doctor,
                type,
                date_time: dateTime,
                location
            })
        });
        
        if (!response.ok) throw new Error('Failed to add appointment');
        
        document.getElementById('appointmentDoctor').value = '';
        document.getElementById('appointmentDateTime').value = '';
        document.getElementById('appointmentLocation').value = '';
        
        await loadAppointments();
        updateStatistics();
        showToast('Appointment scheduled!');
    } catch (error) {
        console.error('Error adding appointment:', error);
        showToast('Failed to schedule appointment');
    }
}

function renderAppointments() {
    const list = document.getElementById('appointmentList');
    
    if (appointments.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📅</div>
                <div class="empty-state-text">No appointments scheduled</div>
            </div>
        `;
        return;
    }
    
    list.innerHTML = appointments.map(apt => {
        const aptDate = new Date(apt.date_time);
        const now = new Date();
        const isPast = aptDate < now;
        
        return `
            <div class="list-item">
                <div class="list-item-header">
                    <span class="list-item-title">${apt.doctor}</span>
                    ${isPast ? '<span class="badge badge-danger">Past</span>' : '<span class="badge badge-success">Upcoming</span>'}
                </div>
                <div class="list-item-content">
                    <p><strong>Type:</strong> ${apt.type}</p>
                    <p><strong>Date & Time:</strong> ${formatDateTime(apt.date_time)}</p>
                    <p><strong>Location:</strong> ${apt.location || 'Not specified'}</p>
                </div>
                <div class="list-item-actions">
                    <button class="btn btn-danger" onclick="deleteAppointment(${apt.id})">Delete</button>
                </div>
            </div>
        `;
    }).join('');
}

async function deleteAppointment(id) {
    if (!confirm('Are you sure you want to delete this appointment?')) return;
    
    try {
        const response = await fetch(`${API_URL}/appointments/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Failed to delete appointment');
        
        await loadAppointments();
        updateStatistics();
        showToast('Appointment deleted');
    } catch (error) {
        console.error('Error deleting appointment:', error);
        showToast('Failed to delete appointment');
    }
}

// ==================== UTILITY FUNCTIONS ====================

function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
    };
    return date.toLocaleString('en-US', options);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
    };
    return date.toLocaleString('en-US', options);
}