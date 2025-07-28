// Personenverwaltung JavaScript - Implementierung nach Klassendiagramm

// Person Klasse
class Person {
    constructor(vorname, nachname, geburtsdatum, email) {
        this.id = this.generateId();
        this.vorname = vorname;
        this.nachname = nachname;
        this.geburtsdatum = new Date(geburtsdatum);
        this.email = email;
    }

    generateId() {
        return Date.now().toString() + Math.random().toString(36).substr(2, 9);
    }

    updateDetails(vorname, nachname, geburtsdatum, email) {
        this.vorname = vorname;
        this.nachname = nachname;
        this.geburtsdatum = new Date(geburtsdatum);
        this.email = email;
    }

    getFormattedBirthdate() {
        return this.geburtsdatum.toLocaleDateString('de-DE');
    }

    getAge() {
        const heute = new Date();
        let alter = heute.getFullYear() - this.geburtsdatum.getFullYear();
        const monatDiff = heute.getMonth() - this.geburtsdatum.getMonth();
        if (monatDiff < 0 || (monatDiff === 0 && heute.getDate() < this.geburtsdatum.getDate())) {
            alter--;
        }
        return alter;
    }
}

// PersonManager Klasse
class PersonManager {
    constructor() {
        this.personen = [];
        this.loadFromStorage();
    }

    addPerson(person) {
        this.personen.push(person);
        this.saveToStorage();
    }

    removePerson(id) {
        this.personen = this.personen.filter(person => person.id !== id);
        this.saveToStorage();
    }

    getPerson(id) {
        return this.personen.find(person => person.id === id);
    }

    updatePerson(updatedPerson) {
        const index = this.personen.findIndex(person => person.id === updatedPerson.id);
        if (index !== -1) {
            this.personen[index] = updatedPerson;
            this.saveToStorage();
        }
    }

    loadFromStorage() {
        const gespeichertePersonen = localStorage.getItem('personen');
        if (gespeichertePersonen) {
            const personenData = JSON.parse(gespeichertePersonen);
            this.personen = personenData.map(data => {
                const person = new Person(data.vorname, data.nachname, data.geburtsdatum, data.email);
                person.id = data.id;
                return person;
            });
        }
    }

    saveToStorage() {
        localStorage.setItem('personen', JSON.stringify(this.personen));
    }

    getAllPersons() {
        return this.personen;
    }
}

// ListViewPage Klasse
class ListViewPage {
    constructor(manager) {
        this.manager = manager;
        this.currentEditId = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const form = document.getElementById('personenForm');
        const cancelBtn = document.getElementById('cancelEdit');

        form.addEventListener('submit', (e) => this.handleAdd(e));
        cancelBtn.addEventListener('click', () => this.cancelEdit());
    }

    render() {
        const liste = document.getElementById('personenListe');
        liste.innerHTML = '';

        this.manager.getAllPersons().forEach(person => {
            const listItem = document.createElement('li');
            listItem.className = 'person-item';
            
            // Person Info Container
            const personInfo = document.createElement('div');
            personInfo.className = 'person-info';
            personInfo.innerHTML = `
                <div class="person-name">${person.vorname} ${person.nachname}</div>
                <div class="person-email">${person.email}</div>
            `;
            
            // Aktions Container
            const personActions = document.createElement('div');
            personActions.className = 'person-actions';
            
            // Bearbeiten Button
            const editBtn = document.createElement('button');
            editBtn.className = 'edit-btn';
            editBtn.textContent = 'Bearbeiten';
            
            // Löschen Button
            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.textContent = 'Löschen';
            
            // Event-Listener direkt anhängen
            personInfo.addEventListener('click', () => {
                this.handleSelect(person.id); // UML-konforme Methode verwenden
            });
            
            editBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.handleEdit(person.id);
            });
            
            deleteBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.handleDelete(person.id);
            });
            
            personActions.appendChild(editBtn);
            personActions.appendChild(deleteBtn);
            
            listItem.appendChild(personInfo);
            listItem.appendChild(personActions);
            liste.appendChild(listItem);
        });
    }

    handleAdd(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const vorname = formData.get('vorname');
        const nachname = formData.get('nachname');
        const geburtsdatum = formData.get('geburtsdatum');
        const email = formData.get('email');

        if (this.currentEditId) {
            // Bearbeiten
            const person = this.manager.getPerson(this.currentEditId);
            if (person) {
                person.updateDetails(vorname, nachname, geburtsdatum, email);
                this.manager.updatePerson(person);
            }
            this.cancelEdit();
        } else {
            // Neue Person hinzufügen
            const neuePerson = new Person(vorname, nachname, geburtsdatum, email);
            this.manager.addPerson(neuePerson);
        }

        this.clearForm();
        this.render();
    }

    handleDelete(id) {
        const person = this.manager.getPerson(id);
        if (!person) {
            console.log('Person nicht gefunden:', id);
            return;
        }
        
        console.log('Lösche Person:', person.vorname, person.nachname);
        
        // Option 1: Direkt löschen ohne Bestätigung
        this.manager.removePerson(id);
        this.render();
        console.log('Person erfolgreich gelöscht');
        
        // Option 2: Inline-Bestätigung (falls gewünscht, einfach auskommentieren)
        // this.showInlineDeleteConfirmation(id);
    }
    
    showInlineDeleteConfirmation(id) {
        // Finde den entsprechenden Listeneintrag
        const personItems = document.querySelectorAll('.person-item');
        const person = this.manager.getPerson(id);
        
        personItems.forEach(item => {
            const personInfo = item.querySelector('.person-info');
            if (personInfo && personInfo.textContent.includes(`${person.vorname} ${person.nachname}`)) {
                const actionsDiv = item.querySelector('.person-actions');
                
                // Ersetze temporär die Buttons
                actionsDiv.innerHTML = `
                    <button class="delete-confirm-btn" style="background-color: #dc3545;">Wirklich löschen?</button>
                    <button class="delete-cancel-btn" style="background-color: #6c757d;">Abbrechen</button>
                `;
                
                // Event-Listener für Bestätigung
                actionsDiv.querySelector('.delete-confirm-btn').addEventListener('click', () => {
                    this.manager.removePerson(id);
                    this.render();
                });
                
                // Event-Listener für Abbruch
                actionsDiv.querySelector('.delete-cancel-btn').addEventListener('click', () => {
                    this.render(); // Zurück zum normalen Zustand
                });
            }
        });
    }

    handleEdit(id) {
        const person = this.manager.getPerson(id);
        if (person) {
            this.currentEditId = id;
            this.fillForm(person);
            this.showEditMode();
        }
    }

    // UML-konforme Methode: handleSelect(id) 
    handleSelect(id) {
        // Wechselt zur Detailansicht der ausgewählten Person
        detailPage.showDetails(id);
    }

    fillForm(person) {
        document.getElementById('vorname').value = person.vorname;
        document.getElementById('nachname').value = person.nachname;
        document.getElementById('geburtsdatum').value = person.geburtsdatum.toISOString().split('T')[0];
        document.getElementById('email').value = person.email;
    }

    showEditMode() {
        document.querySelector('input[type="submit"]').value = 'Änderungen speichern';
        document.getElementById('cancelEdit').style.display = 'inline-block';
    }

    cancelEdit() {
        this.currentEditId = null;
        this.clearForm();
        document.querySelector('input[type="submit"]').value = 'Person hinzufügen';
        document.getElementById('cancelEdit').style.display = 'none';
    }

    clearForm() {
        document.getElementById('personenForm').reset();
    }

    showListView() {
        document.getElementById('listView').style.display = 'block';
        document.getElementById('detailView').style.display = 'none';
        this.render();
    }
}

// DetailPage Klasse
class DetailPage {
    constructor(manager) {
        this.manager = manager;
        this.currentPerson = null; // entspricht 'person' im UML
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        document.getElementById('editPerson').addEventListener('click', () => this.handleEdit());
        document.getElementById('backToList').addEventListener('click', () => this.handleBack());
    }

    showDetails(id) {
        this.currentPerson = this.manager.getPerson(id);
        if (this.currentPerson) {
            this.render();
            document.getElementById('listView').style.display = 'none';
            document.getElementById('detailView').style.display = 'block';
        }
    }

    render() {
        if (!this.currentPerson) return;

        const detailsContainer = document.getElementById('personDetails');
        detailsContainer.innerHTML = `
            <div class="detail-item">
                <div class="detail-label">Vorname:</div>
                <div class="detail-value">${this.currentPerson.vorname}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Nachname:</div>
                <div class="detail-value">${this.currentPerson.nachname}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Geburtsdatum:</div>
                <div class="detail-value">${this.currentPerson.getFormattedBirthdate()}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Alter:</div>
                <div class="detail-value">${this.currentPerson.getAge()} Jahre</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">E-Mail:</div>
                <div class="detail-value">${this.currentPerson.email}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">ID:</div>
                <div class="detail-value">${this.currentPerson.id}</div>
            </div>
        `;
    }

    // UML-konforme Methode: handleSave() 
    handleSave() {
        if (this.currentPerson) {
            // Speichern wird über den PersonManager abgewickelt
            this.manager.updatePerson(this.currentPerson);
            console.log('Person gespeichert:', this.currentPerson.vorname, this.currentPerson.nachname);
        }
    }

    // UML-konforme Methode: handleCancel()
    handleCancel() {
        // Zurück zur Listenansicht ohne Änderungen
        this.handleBack();
    }

    handleEdit() {
        if (this.currentPerson) {
            listViewPage.handleEdit(this.currentPerson.id);
            this.handleBack();
        }
    }

    handleBack() {
        listViewPage.showListView();
    }
}

// Anwendung initialisieren
const personManager = new PersonManager();
const listViewPage = new ListViewPage(personManager);
const detailPage = new DetailPage(personManager);

// Erste Renderung
document.addEventListener('DOMContentLoaded', () => {
    listViewPage.render();
});
