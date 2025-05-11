<template>
  <v-container class="manual-container">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold mb-6">Sesplan User Manual</h1>
        <p class="mb-2">
          <router-link to="/">&laquo; Back to Sesplan Home</router-link>
        </p>
        <p class="text-caption mb-4"><em>This manual is valid for Sesplan application version 0.1.x.</em></p>
        <p class="mb-8">Welcome to the Sesplan User Manual. This guide will help you understand how to navigate and effectively use the Sesplan application for your RPG campaign planning.</p>

        <!-- Table of Contents -->
        <v-card variant="outlined" class="mb-10 pa-4 sticky-toc">
          <h2 class="text-h6 font-weight-medium mb-3">Table of Contents</h2>
          <ul class="table-of-contents">
            <li><a @click="scrollTo('introduction')">1. Introduction</a></li>
            <li><a @click="scrollTo('registration-login')">2. Registration and Login</a></li>
            <li><a @click="scrollTo('dashboard-overview')">3. Dashboard Overview</a></li>
            <li><a @click="scrollTo('managing-worlds')">4. Creating and Managing Worlds</a></li>
            <li><a @click="scrollTo('campaigns')">5. Creating and Managing Campaigns</a></li>
            <li><a @click="scrollTo('characters')">6. Managing Characters</a></li>
            <li><a @click="scrollTo('sessions')">7. Planning and Managing Sessions</a></li>
            <li><a @click="scrollTo('locations')">8. Detailing Locations</a></li>
            <li><a @click="scrollTo('items')">9. Cataloging Items</a></li>
            <li><a @click="scrollTo('organizations')">10. Tracking Organizations</a></li>
            <li><a @click="scrollTo('journals')">11. Writing Journals & Notes</a></li>
            <li><a @click="scrollTo('settings')">12. User Account Settings</a></li>
            <li><a @click="scrollTo('markdown-editor')">13. Note on Markdown Editor</a></li>
          </ul>
        </v-card>

        <v-divider class="mb-10"></v-divider>

        <section id="introduction">
          <h2 class="text-h4 mt-6 mb-3">1. Introduction</h2>
          <p>Sesplan is a comprehensive application designed to streamline the planning and management of your tabletop role-playing game (RPG) campaigns. It provides tools for Game Masters (GMs) and players to organize game worlds, create detailed characters, plan sessions, track plotlines, and collaborate effectively.</p>
          <p>Our goal is to provide an intuitive and powerful platform so you can focus more on storytelling and less on administrative tasks.</p>
        </section>

        <v-divider class="my-10"></v-divider>

        <section id="registration-login">
          <h2 class="text-h4 mt-6 mb-3">2. Registration and Login</h2>
          <p>To access the full features of Sesplan, you must first create an account and log in.</p>
          
          <h3 class="text-h6 font-weight-medium mt-6 mb-3">2.1. Registration</h3>
          <ol class="manual-list">
            <li>Navigate to the <router-link to="/register">Registration Page</router-link> by clicking the "Sign Up" or "Register" button on the landing page.</li>
            <li>You will be presented with a registration form. Please fill in the following details:
              <ul>
                <li><strong>Username:</strong> Choose a unique username (minimum 3 characters).</li>
                <li><strong>Email:</strong> Provide a valid email address. This will be used for account recovery and important notifications.</li>
                <li><strong>Password:</strong> Choose a secure password (minimum 6 characters).</li>
                <li><strong>Confirm Password:</strong> Re-enter your chosen password to ensure it matches.</li>
              </ul>
            </li>
            <li>Once you have filled in all the required fields correctly, click the "Register" button.</li>
            <li>After successful registration, you will see a success message and will be automatically redirected to the Login page after a short delay. Currently, email confirmation is not a required step to activate your account.</li>
          </ol>
          
          <h3 class="text-h6 font-weight-medium mt-6 mb-3">2.2. Login</h3>
          <ol class="manual-list">
            <li>Go to the <router-link to="/login">Login Page</router-link>.</li>
            <li>Enter your registered <strong>Username</strong> and <strong>Password</strong>.</li>
            <li>Click the "Login" button.</li>
            <li>If your credentials are correct, you will be redirected to your personal dashboard.</li>
          </ol>
          <p class="mt-4"><strong>Forgot your password?</strong> The application does not currently feature an automated password reset function on the login page. Please ensure you store your password securely. For assistance, you might need to contact support if available.</p>
        </section>

        <v-divider class="my-10"></v-divider>

        <section id="dashboard-overview">
          <h2 class="text-h4 mt-6 mb-3">3. Dashboard Overview</h2>
          <p>Upon successful login, you will be directed to your main Dashboard. The Dashboard serves as your primary workspace within Sesplan.</p>
          <p>The main components of the Dashboard interface are:</p>
          <ul class="manual-list">
            <li><strong>Sidebar:</strong> Located on the left (can be collapsed/expanded), the Sidebar provides primary navigation to different sections of the application. It includes links to:
              <ul>
                <li><strong>Dashboard Home (Logo/Sesplan Name):</strong> Returns you to the main dashboard welcome screen.</li>
                <li><strong>Worlds:</strong> Access and manage your game worlds.</li>
                <li><strong>Campaigns:</strong> View and manage your campaigns.</li>
                <li><strong>Sessions:</strong> Access your list of game sessions.</li>
                <li><strong>Characters:</strong> Manage your player characters and NPCs.</li>
                <li><strong>Journals:</strong> Access your journals and notes.</li>
              </ul>
            </li>
            <li><strong>Header:</strong> Located at the top, the Header contains a mobile toggle for the sidebar and a user profile section on the right. The user profile section displays your username and an avatar (first letter of username). Clicking on it reveals a dropdown menu with:
                <ul>
                    <li><strong>Settings:</strong> Navigates to your user account settings page.</li>
                    <li><strong>Logout:</strong> Logs you out of the application.</li>
                </ul>
            </li>
            <li><strong>Main Content Area:</strong> This is where the content for the selected section (e.g., Worlds list, Campaign details) is displayed. The default view after login (`DashboardHomeView.vue`) currently shows a welcome message and a link to the Sesplan Discord server for feedback.</li>
          </ul>
          <p>Familiarize yourself with these elements to efficiently navigate and use Sesplan.</p>
        </section>

        <v-divider class="my-10"></v-divider>

        <section id="managing-worlds">
          <h2 class="text-h4 mt-6 mb-3">4. Creating and Managing Worlds</h2>
          <p>In Sesplan, "Worlds" are the foundational containers for your RPG settings. Each world is a distinct universe where your stories unfold, holding all related information such as lore, locations, characters, items, and the campaigns that take place within it.</p>
          
          <h3 class="text-h6 font-weight-medium mt-6 mb-3">4.1. Accessing the Worlds Section</h3>
          <p>After logging in, click on "Worlds" in the Sidebar. This will take you to the Worlds overview page (`WorldsView.vue`), where all your created worlds are listed.</p>

          <h3 class="text-h6 font-weight-medium mt-6 mb-3">4.2. Creating a New World</h3>
          <ol class="manual-list">
            <li>On the Worlds overview page, look for a button labeled "Create New World".</li>
            <li>Clicking this button will open a dialog (`WorldForm.vue`) where you need to provide:
              <ul>
                <li><strong>Name:</strong> A unique and descriptive name for your world. This is a required field.</li>
                <li><strong>Description (Optional):</strong> A brief overview or summary of your world. This field might not be directly in the initial creation form but can be edited later (see 4.3).</li>
              </ul>
            </li>
            <li>After filling in the name, click "Save" or a similar confirmation button in the dialog.</li>
            <li>Your new world will now appear in your list of worlds on the `WorldsView.vue` page.</li>
          </ol>

          <h3 class="text-h6 font-weight-medium mt-6 mb-3">4.3. Viewing and Managing an Existing World</h3>
          <p>From the Worlds overview page, click on the name of a world or a "View Details" button associated with it. This will navigate you to its detail page (`WorldDetailView.vue`).</p>
          <p>The World Detail Page is your central hub for everything related to that specific world. It uses a tabbed interface:</p>
          <ul class="manual-list">
            <li><strong>Details Tab (`WorldDetailsTab.vue`):</strong>
                <ul>
                    <li>Displays the world's name (editable via a header component, likely `WorldDetailHeader.vue`).</li>
                    <li>Allows editing of the <strong>Description</strong> using a Markdown editor.</li>
                    <li>Shows non-editable information like "Public" status, "Created" date, and "Last Updated" date.</li>
                </ul>
            </li>
            <li><strong>Characters Tab:</strong> Lists characters belonging to this world. You can add, edit (via `CreateCharacterForm.vue` dialog), delete, and potentially generate characters using AI. Clicking a character row may navigate to `CharacterDetailView.vue`.</li>
            <li><strong>Locations Tab:</strong> Lists locations within this world. You can add, edit (via `CreateLocationForm.vue` dialog), delete, and potentially generate locations using AI. Clicking a location row navigates to `LocationDetailView.vue`.</li>
            <li><strong>Organizations Tab:</strong> Lists organizations in this world. You can add, edit (via `CreateOrganizationForm.vue` dialog), delete, and potentially generate organizations using AI. Clicking an organization row navigates to `OrganizationDetailView.vue`.</li>
            <li><strong>Items Tab:</strong> Lists items found in this world. You can add, edit (via `CreateItemForm.vue` dialog), delete, and potentially generate items using AI. Clicking an item row navigates to `ItemDetailView.vue`.</li>
          </ul>
          <p>A "Delete World" button is also available on the `WorldDetailHeader.vue` (Use with extreme caution!).</p>
        </section>

        <v-divider class="my-10"></v-divider>

        <section id="managing-campaigns">
          <h2 id="campaigns" class="text-h4 mt-6 mb-3">5. Managing Campaigns</h2>
          <p>Campaigns are the heart of your adventures, linking worlds, stories, and players together. Here's how to manage them effectively:</p>

          <v-list-item-title class="text-h5 my-3">5.1 Creating a New Campaign</v-list-item-title>
          <p>
            From your dashboard, navigate to the "Campaigns" section (usually found in the sidebar). You'll see a list of your existing campaigns.
            To create a new one:
          </p>
          <ol>
            <li>Click the "<strong>Add New Campaign</strong>" button. This will open a creation dialog.</li>
            <li>Fill in the following details for your campaign:
              <ul>
                <li><strong>World:</strong> Select an existing world from the dropdown list. This is a required field, as every campaign must be associated with a world.</li>
                <li><strong>Name:</strong> Enter a clear and descriptive name for your campaign (e.g., "The Dragon's Curse"). This field is required.</li>
                <li><strong>Description:</strong> Provide a summary of your campaign's plot, theme, or any other relevant details. This field uses a <a href="#markdown-editor">Markdown editor</a> for rich text formatting.</li>
              </ul>
            </li>
            <li>Click "<strong>Create Campaign</strong>" to save your new campaign.</li>
          </ol>
          <p class="mt-2"><em>Note: Fields like start/end dates or cover images are not currently supported for campaigns.</em></p>

          <v-list-item-title class="text-h5 my-3">5.2 Viewing and Editing Campaign Details</v-list-item-title>
          <p>
            To view or edit a campaign, click on its name in the campaign list. This will take you to the Campaign Detail page, which is organized into several tabs:
          </p>
          <ul class="my-3">
            <li>
              <strong>Header Information:</strong>
              <ul>
                <li>The campaign's name is displayed at the top. If you are the Game Master (GM) of the campaign, you can click an edit icon next to the name to change it directly.</li>
              </ul>
            </li>
            <li>
              <strong>Details Tab:</strong>
              <ul>
                <li><strong>Description:</strong> Shows the full campaign description. If you are the GM, you can edit this using the <a href="#markdown-editor">Markdown editor</a>.</li>
                <li><strong>World:</strong> Displays the name of the world this campaign is linked to.</li>
                <li><strong>Created:</strong> The date the campaign was created.</li>
                <li><strong>Last Updated:</strong> The date the campaign was last modified.</li>
                <li><strong>Owner (GM):</strong> The username of the user who owns and manages the campaign.</li>
              </ul>
            </li>
            <li>
              <strong>Session Tab:</strong> (Primarily for the GM)
              <ul>
                <li>Lists all game sessions associated with this campaign. Each session entry may show its title, date/time, a brief description, and summary.</li>
                <li>As the GM, you can:
                  <ul>
                    <li><strong>Add New Session:</strong> Opens a dialog to create a new session with fields for Title (required), Date & Time (optional), Description (optional, using a simple text area), and Summary (optional, using a simple text area).</li>
                    <li><strong>Edit Session:</strong> Modify the details of an existing session.</li>
                    <li><strong>Delete Session:</strong> Remove a session from the campaign.</li>
                  </ul>
                </li>
                <li>Clicking on a session title will navigate you to the <a href="#sessions">Session Detail view</a> (if implemented and linked).</li>
              </ul>
            </li>
            <li>
              <strong>Members Tab:</strong>
              <ul>
                <li>Lists all users (players and GMs) who are part of this campaign, showing their username, email, and role within the campaign (e.g., GM, Player).</li>
                <li>If you are the GM, you can:
                  <ul>
                    <li><strong>Edit Role:</strong> Change the role of a member (e.g., promote a player to GM, though typically a campaign has one primary GM).</li>
                    <li><strong>Remove Member:</strong> Remove a user from the campaign.</li>
                  </ul>
                </li>
                <li><em>This section manages user participation, not the in-game characters they play. For managing game characters, see <a href="#worlds">Managing Worlds</a> and its "Characters" tab.</em></li>
              </ul>
            </li>
            <li>
              <strong>Invites Tab:</strong> (Primarily for the GM)
              <ul>
                <li>Lists pending invitations for users to join the campaign.</li>
                <li>As the GM, you can:
                  <ul>
                    <li><strong>Invite User:</strong> Opens a dialog to send an invitation to a user via their email address.</li>
                    <li><strong>Manage Invites:</strong> Revoke or resend pending invitations.</li>
                  </ul>
                </li>
              </ul>
            </li>
          </ul>
          <p>
            Always remember to save any changes you make.
          </p>

          <v-list-item-title class="text-h5 my-3">5.3 Key Campaign Management Actions (Summary)</v-list-item-title>
          <ul>
            <li><strong>Creation:</strong> Define name, description, and link to a world.</li>
            <li><strong>Information Hub:</strong> The "Details" tab provides an overview of the campaign's core information.</li>
            <li><strong>Session Planning:</strong> The "Session" tab allows the GM to schedule and outline game sessions.</li>
            <li><strong>Player Management:</strong> The "Members" tab is for managing who is part of the campaign and their roles.</li>
            <li><strong>Growing Your Group:</strong> The "Invites" tab helps GMs bring new players into the campaign.</li>
          </ul>
        </section>

        <v-divider class="my-5"></v-divider>

        <section id="characters-section">
          <h2 id="characters" class="text-h4 mt-6 mb-3">6. Managing Characters</h2>
          <p>
            Characters are the protagonists of your stories, each with unique traits and a history. Sesplan allows you to create and manage characters primarily within the context of a specific World.
          </p>

          <v-list-item-title class="text-h5 my-3">6.1 Creating a New Character</v-list-item-title>
          <p>There are two main ways to create a new character:</p>
          <ol class="mb-3">
            <li>
              <strong>From the "My Characters" Page:</strong>
              <ul>
                <li>Navigate to "My Characters" from the dashboard sidebar.</li>
                <li>Click the "<strong>Add New Character</strong>" button.</li>
                <li>You will first be prompted to select the <strong>World</strong> this character will belong to from a list of worlds you own. Characters must always be associated with a world.</li>
                <li>Once a world is selected, a form will appear asking for:
                  <ul>
                    <li><strong>Name:</strong> The character's name (required).</li>
                    <li><strong>Description:</strong> A detailed background, personality traits, etc., using the <a href="#markdown-editor">Markdown editor</a>.</li>
                    <li><strong>Assign User (Optional, if you own the world):</strong> You can assign this character to another registered user who is, for example, a player in one of your campaigns in that world. If you don't assign a user, the character will be considered yours.</li>
                  </ul>
                </li>
                <li>Click "<strong>Create Character</strong>" to save.</li>
              </ul>
            </li>
            <li class="mt-2">
              <strong>From a World's Detail Page:</strong>
              <ul>
                <li>Navigate to the specific <a href="#worlds">World</a> where you want to create the character.</li>
                <li>Go to the "<strong>Characters</strong>" tab.</li>
                <li>Click the "Add Character" (or similar) button.</li>
                <li>The same character creation form will appear (Name, Description, Assign User if you own the world). The world context is already set.</li>
              </ul>
            </li>
          </ol>
          <p><em>Note: Character tags are not assigned during initial creation via this form but are managed later in the Character Detail view.</em></p>

          <v-list-item-title class="text-h5 my-3">6.2 Viewing and Editing Character Details</v-list-item-title>
          <p>
            You can access a character's detail page by clicking their name in the "My Characters" list or from the "Characters" tab within a World's detail page.
            The Character Detail view (`CharacterDetailView.vue`) provides comprehensive information and management options:
          </p>
          <ul class="my-3">
            <li>
              <strong>Header & Basic Info:</strong>
              <ul>
                <li><strong>Name:</strong> The character's name is displayed.</li>
                <li>An "<strong>Edit Character</strong>" button opens a modal with the same form used for creation (Name, Description, Assign User), allowing you to modify these core details.</li>
                <li>A link back to the "Characters" tab of the associated World.</li>
              </ul>
            </li>
            <li>
              <strong>Main Details Section:</strong>
              <ul>
                <li><strong>Description:</strong> The character's full description is displayed. You can edit this inline using a <a href="#markdown-editor">Markdown editor</a> by clicking the pencil icon.</li>
                <li><strong>World:</strong> Displays the name of the world the character belongs to (links to the World's detail page).</li>
                <li><strong>Owner:</strong> Shows the username of the user this character is assigned to (or the creator if unassigned).</li>
                <li><strong>Created / Last Updated:</strong> Timestamps for character creation and modification.</li>
              </ul>
            </li>
            <li>
              <strong>Character Tags Section:</strong>
              <ul>
                <li>Displays any tags currently assigned to the character (e.g., "Race: Elf", "Class: Mage").</li>
                <li>An "<strong>Edit Tags</strong>" button opens a dialog where you can assign or unassign tags to the character. Tags are selected from a list of "Character Tag Types" predefined for the world.</li>
              </ul>
            </li>
            <li>
              <strong>Manage Character Tag Types Section:</strong> (Typically for World Owners)
              <ul>
                <li>This section allows for the creation and management of the available "Character Tag Types" for the current world. For example, you could create tag types like "Class," "Race," "Skill," or "Status Effect."</li>
                <li>You can add new tag types, edit their names, or delete them. These defined tag types then become available for assignment to any character within that world.</li>
              </ul>
            </li>
            <li>
              <strong>Journal Section:</strong>
              <ul>
                <li>Integrates with the character's personal journal entries (see <a href="#journals">Managing Journals</a>). Displays relevant entries and may allow for creating new ones.</li>
              </ul>
            </li>
            <li>
              <strong>Items Section:</strong>
              <ul>
                <li>Lists all <a href="#items">items</a> currently owned or equipped by the character.</li>
                <!-- Add details on managing items for characters if functionality exists -->
              </ul>
            </li>
          </ul>

          <v-list-item-title class="text-h5 my-3">6.3 Deleting a Character</v-list-item-title>
          <p>
            Characters can be deleted either from the "My Characters" list (via a "Delete" button next to the character) or potentially from within the World's "Characters" tab. A confirmation dialog will appear before the character is permanently removed.
          </p>
        </section>

        <v-divider class="my-10"></v-divider>

        <section id="sessions-section">
          <h2 id="sessions" class="text-h4 mt-6 mb-3">7. Managing Sessions</h2>
          <p>
            Game sessions are individual play instances within a campaign. Sesplan helps you schedule these sessions and coordinate player availability.
          </p>

          <v-list-item-title class="text-h5 my-3">7.1 Creating, Editing, and Deleting Sessions</v-list-item-title>
          <p>
            The primary management of sessions (creating, editing details, and deleting) occurs within the context of a specific <a href="#campaigns">Campaign</a>:
          </p>
          <ol class="mb-3">
            <li>Navigate to the desired campaign's detail page.</li>
            <li>Go to the "<strong>Session</strong>" tab.</li>
            <li>Here, the Game Master (GM) of the campaign can:
              <ul>
                <li><strong>Add New Session:</strong> Click the "Add Session" button. A dialog will appear prompting for:
                  <ul>
                    <li><strong>Title:</strong> A name for the session (e.g., "Chapter 3: The Cursed Tomb"). This is required.</li>
                    <li><strong>Date & Time (Optional):</strong> Use the date-time picker to schedule the session.</li>
                    <li><strong>Description (Optional):</strong> A brief plan or teaser for the session.</li>
                    <li><strong>Summary (Optional):</strong> A place to recap what happened after the session concludes.</li>
                  </ul>
                </li>
                <li><strong>Edit Session:</strong> Modify the details of an existing session using a similar dialog.</li>
                <li><strong>Delete Session:</strong> Remove a session. A confirmation will be required.</li>
              </ul>
            </li>
          </ol>

          <v-list-item-title class="text-h5 my-3">7.2 Viewing Your Sessions List</v-list-item-title>
          <p>
            You can see a consolidated list of all sessions you are part of (either as a GM or a player) by navigating to "<strong>My Sessions</strong>" from the main dashboard sidebar. This view (`SessionListView.vue`) typically shows:
          </p>
          <ul class="my-3">
            <li>The session title.</li>
            <li>The name of the campaign it belongs to.</li>
            <li>The scheduled date and time.</li>
          </ul>
          <p>Clicking on a session in this list will take you to its Session Detail page. No management actions (create, edit, delete) are available from this global list.</p>

          <v-list-item-title class="text-h5 my-3">7.3 Session Detail View & Availability Planning</v-list-item-title>
          <p>
            The Session Detail page (`SessionDetailView.vue`) provides specific information about a single session and is the hub for availability planning:
          </p>
          <ul class="my-3">
            <li><strong>Information Displayed:</strong>
              <ul>
                <li>Session Title</li>
                <li>Link back to the parent Campaign</li>
                <li>Scheduled Date & Time</li>
                <li>Session Description (if provided)</li>
                <li>Session Summary (if provided)</li>
                <li>Creation and Last Updated dates</li>
              </ul>
            </li>
            <li>
              <strong>Availability Planning:</strong> This is a key feature of the session detail view.
              <ul>
                <li><strong>For Game Masters (GMs):</strong>
                  <ul>
                    <li>GMs can define one or more proposed <strong>time slots</strong> for the session (e.g., "Friday 7-11 PM", "Saturday 2-6 PM"). This is done using the "Manage time slots" interface.</li>
                  </ul>
                </li>
                <li><strong>For All Campaign Members (GMs and Players):</strong>
                  <ul>
                    <li>Once time slots are defined by the GM, an <strong>Availability Grid</strong> is displayed.</li>
                    <li>Each campaign member can mark their availability (e.g., Yes, No, Maybe) for each proposed time slot.</li>
                    <li>This helps the GM determine the best time to run the session based on player responses.</li>
                  </ul>
                </li>
              </ul>
            </li>
            <li>
              <strong>Assigned Characters (Note):</strong> Functionality to assign specific player characters to a session appears to be planned but was observed to be commented out in the code. If implemented, GMs would manage this here.
            </li>
          </ul>
          <p><em>Direct editing of session details (like title or description) is not done on this page but through the "Session" tab of the parent campaign.</em></p>
        </section>

        <v-divider class="my-10"></v-divider>
        
        <section id="locations-section">
          <h2 id="locations" class="text-h4 mt-6 mb-3">8. Managing Locations</h2>
          <p>
            Locations bring your worlds to life, from sprawling cities to hidden dungeons. Sesplan enables you to define, categorize, and hierarchize these places.
          </p>

          <v-list-item-title class="text-h5 my-3">8.1 Creating and Managing Locations within a World</v-list-item-title>
          <p>
            Locations are managed exclusively within a specific <a href="#worlds">World</a>. To add, view, or manage locations:
          </p>
          <ol class="mb-3">
            <li>Navigate to the detail page of the World you want to work with.</li>
            <li>Select the "<strong>Locations</strong>" tab.</li>
            <li>This tab displays a list of all locations within that world, often in a table format (`WorldEntityTable.vue`).</li>
            <li>From here, you can:
              <ul>
                <li><strong>Add New Location:</strong> Clicking an "Add" or "Create Location" button opens the `CreateLocationForm.vue` dialog.</li>
                <li><strong>Edit Location:</strong> Select a location and click an "Edit" button to open the same form populated with its data.</li>
                <li><strong>Delete Location:</strong> Remove a location (a confirmation will be required).</li>
                <li><strong>Generate with AI:</strong> Some views may offer an option to generate location details using AI.</li>
              </ul>
            </li>
          </ol>
          <p>The <strong>Location Creation/Editing Form</strong> (`CreateLocationForm.vue`) includes the following fields:</p>
          <ul class="my-3">
            <li><strong>Name:</strong> The name of the location (e.g., "Whispering Woods," "The Rusty Mug Tavern"). This field is required.</li>
            <li><strong>Description:</strong> A detailed description of the location, its atmosphere, notable features, etc. This uses a <a href="#markdown-editor">Markdown editor</a>.</li>
            <li><strong>Parent Location:</strong> You can select another existing location within the same world to be the parent of this one, creating a hierarchy (e.g., "The Rusty Mug Tavern" could be a child of "Port Town Market District"). This helps organize complex areas.</li>
            <li><strong>Tags:</strong> Assign relevant tags to categorize the location (e.g., "Forest," "Tavern," "Ruins"). Tags are chosen from a list of "Location Tag Types" predefined for the world.</li>
          </ul>

          <v-list-item-title class="text-h5 my-3">8.2 Location Detail View</v-list-item-title>
          <p>
            Clicking on a location's name in the list (from the World's "Locations" tab) will take you to its dedicated detail page (`LocationDetailView.vue`). This view provides:
          </p>
          <ul class="my-3">
            <li><strong>Header:</strong> The location's name, a button to go back to the World view, and an "<strong>Edit Location</strong>" button (which opens the `CreateLocationForm.vue` for full editing).</li>
            <li>
              <strong>Main Details:</strong>
              <ul>
                <li><strong>Description:</strong> Displayed and editable inline using a <a href="#markdown-editor">Markdown editor</a> (via a pencil icon).</li>
                <li><strong>Parent Location:</strong> If set, shows the name of the parent location.</li>
                <li><strong>World ID, Created Date, Updated Date.</strong></li>
              </ul>
            </li>
            <li>
              <strong>Tags Section:</strong>
              <ul>
                <li>Displays currently assigned tags.</li>
                <li>An "<strong>Edit Tags</strong>" button opens a dialog allowing you to select/deselect tags from the available "Location Tag Types" for that world.</li>
              </ul>
            </li>
            <li>
              <strong>Manage Location Tag Types Section:</strong> (Typically for World Owners)
              <ul>
                <li>This important section allows you (if you are the world owner or have permissions) to define the actual <strong>types</strong> of tags that can be used for locations within this specific world.</li>
                <li>For example, you could create tag types like "Region Type" (with values like Forest, Mountain, City), "Building Type" (Tavern, Shop, Temple), or "Point of Interest."</li>
                <li>You can Add, Edit, and Delete these tag types. Once defined, these types appear in the "Edit Tags" dialog for individual locations.</li>
              </ul>
            </li>
          </ul>
          <p><em>Note: While locations can have characters and items within them, these are typically managed by assigning a character or item to a location via their respective forms (see <a href="#characters">Managing Characters</a> and <a href="#items">Managing Items</a>), rather than directly adding them from the location detail page.</em></p>
        </section>

        <v-divider class="my-10"></v-divider>

        <section id="items-section">
          <h2 id="items" class="text-h4 mt-6 mb-3">9. Managing Items</h2>
          <p>
            From powerful artifacts to mundane supplies, items are an integral part of any RPG. Sesplan helps you track and detail these items within your worlds.
          </p>

          <v-list-item-title class="text-h5 my-3">9.1 Creating and Managing Items within a World</v-list-item-title>
          <p>
            Items, like locations, are managed exclusively within a specific <a href="#worlds">World</a>. To add, view, or manage items:
          </p>
          <ol class="mb-3">
            <li>Navigate to the detail page of the World you want to work with.</li>
            <li>Select the "<strong>Items</strong>" tab.</li>
            <li>This tab displays a list of all items within that world, often using the `WorldEntityTable.vue` component.</li>
            <li>From here, you can:
              <ul>
                <li><strong>Add New Item:</strong> Clicking an "Add" or "Create Item" button opens the `CreateItemForm.vue` dialog.</li>
                <li><strong>Edit Item:</strong> Select an item and click an "Edit" button to open the same form populated with its data.</li>
                <li><strong>Delete Item:</strong> Remove an item (a confirmation will be required).</li>
                <li><strong>Generate with AI:</strong> An option to generate item details using AI might be available.</li>
              </ul>
            </li>
          </ol>
          <p>The <strong>Item Creation/Editing Form</strong> (`CreateItemForm.vue`) includes the following fields:</p>
          <ul class="my-3">
            <li><strong>Name:</strong> The name of the item (e.g., "Sword of Valor," "Healing Potion"). This field is required.</li>
            <li><strong>Description:</strong> A description of the item, its appearance, abilities, or history. The item detail view supports <a href="#markdown-editor">Markdown</a> for this field.</li>
            <li><strong>Character (Optional):</strong> You can assign the item to an existing character within the same world.</li>
            <li><strong>Location (Optional):</strong> You can place the item in an existing location within the same world.</li>
            <li><strong>Tags:</strong> Assign relevant tags to categorize the item (e.g., "Weapon," "Magic," "Consumable"). Tags are chosen from a list of "Item Tag Types" predefined for the world, selected via checkboxes.</li>
          </ul>

          <v-list-item-title class="text-h5 my-3">9.2 Item Detail View</v-list-item-title>
          <p>
            Clicking on an item's name in the list (from the World's "Items" tab) will take you to its dedicated detail page (`ItemDetailView.vue`). This view provides:
          </p>
          <ul class="my-3">
            <li><strong>Header:</strong> The item's name, a button to go back to the World view, and an "<strong>Edit Item</strong>" button (which opens the `CreateItemForm.vue` for full editing).</li>
            <li>
              <strong>Main Details:</strong>
              <ul>
                <li><strong>Description:</strong> Displayed and editable inline using a <a href="#markdown-editor">Markdown editor</a> (via a pencil icon).</li>
                <li><strong>Assigned Character:</strong> If assigned, shows the ID of the character.</li>
                <li><strong>Assigned Location:</strong> If assigned, shows the ID of the location.</li>
                <li><strong>World ID, Created Date, Updated Date.</strong></li>
              </ul>
            </li>
            <li>
              <strong>Tags Section:</strong>
              <ul>
                <li>Displays currently assigned tags to the item.</li>
                <li>An "<strong>Edit Tags</strong>" button opens a dialog allowing you to select/deselect tags from the available "Item Tag Types" for that world.</li>
              </ul>
            </li>
            <li>
              <strong>Manage Item Tag Types Section:</strong> (Typically for World Owners)
              <ul>
                <li>Similar to locations and characters, this section allows for the creation and management of the <strong>types</strong> of tags that can be used for items within this specific world (e.g., "Weapon Type," "Rarity," "Damage Type").</li>
                <li>You can Add, Edit, and Delete these item tag types. They then become available for assignment to individual items.</li>
              </ul>
            </li>
          </ul>
          <p><em>When editing an item from its detail page, assigning it to a different character might need to be done through the character's inventory management if direct reassignment is not available in the item's edit form in this context.</em></p>
        </section>

        <v-divider class="my-10"></v-divider>

        <section id="organizations-section">
          <h2 id="organizations" class="text-h4 mt-6 mb-3">10. Tracking Organizations</h2>
          <p>
            Guilds, factions, secret societies, and other organizations add layers of intrigue and interaction to your game world. Sesplan allows you to define and track these entities.
          </p>

          <v-list-item-title class="text-h5 my-3">10.1 Creating and Managing Organizations within a World</v-list-item-title>
          <p>
            Organizations are managed within a specific <a href="#worlds">World</a>, similar to locations and items.
          </p>
          <ol class="mb-3">
            <li>Navigate to the detail page of the World you want to work with.</li>
            <li>Select the "<strong>Organizations</strong>" tab.</li>
            <li>This tab lists all organizations within that world, typically using the `WorldEntityTable.vue` component.</li>
            <li>From this list, you can:
              <ul>
                <li><strong>Add New Organization:</strong> Clicking an "Add" or "Create Organization" button opens the `CreateOrganizationForm.vue` dialog.</li>
                <li><strong>Edit Organization:</strong> Select an organization and click an "Edit" button. This reopens the `CreateOrganizationForm.vue` populated with the organization's data, allowing you to change its name, description, and parent organization.</li>
                <li><strong>Delete Organization:</strong> Remove an organization (confirmation required).</li>
                <li><strong>Generate with AI:</strong> An option to generate organization details using AI might be available.</li>
              </ul>
            </li>
          </ol>
          <p>The <strong>Organization Creation/Editing Form</strong> (`CreateOrganizationForm.vue`) includes:</p>
          <ul class="my-3">
            <li><strong>Name:</strong> The name of the organization (e.g., "The Silver Hand," "Shadow Thieves Guild"). Required, max 255 characters.</li>
            <li><strong>Description:</strong> A summary of the organization, its goals, hierarchy, etc. This currently uses a standard text area (Markdown is supported for display and inline editing in the detail view).</li>
            <li><strong>Parent Organization (Optional):</strong> Link to another existing organization to create a hierarchy (e.g., a local chapter under a larger guild).</li>
          </ul>
          <p><em>Note: Unlike locations or items, tags are not assigned during the initial creation of an organization via this form. Tag management is handled within the Organization Detail view.</em></p>

          <v-list-item-title class="text-h5 my-3">10.2 Organization Detail View</v-list-item-title>
          <p>
            Clicking an organization's name in the list takes you to its `OrganizationDetailView.vue`. This page offers:
          </p>
          <ul class="my-3">
            <li><strong>Header:</strong> The organization's name and a button to return to the World view.</li>
            <li>
              <strong>Main Details:</strong>
              <ul>
                <li><strong>Description:</strong> Displayed and editable inline using a <a href="#markdown-editor">Markdown editor</a> (via a pencil icon, if you have permissions).</li>
                <li><strong>Parent Organization:</strong> If set, displays the name of the parent (as a link to its detail page).</li>
                <li><strong>Created Date, Updated Date.</strong></li>
              </ul>
            </li>
            <li>
              <strong>Tag Assignment Section:</strong> (Uses `OrganizationTagAssignment.vue`)
              <ul>
                <li>Displays tags currently assigned to the organization.</li>
                <li>Allows users with permission to assign or unassign tags from a list of "Organization Tag Types" predefined for the world.</li>
              </ul>
            </li>
            <li>
              <strong>Manage Organization Tag Types Button:</strong> (In header, typically for World Owners)
              <ul>
                <li>Opens a modal with the `OrganizationTagTypeManager.vue` component.</li>
                <li>Here, you can define the actual <strong>types</strong> of tags available for organizations in this world (e.g., "Guild Type," "Alignment," "Influence Level"). You can Add, Edit, and Delete these tag types.</li>
              </ul>
            </li>
            <li><strong>Placeholder Sections:</strong> The view includes placeholders for future functionality like listing child organizations and members.</li>
          </ul>
        </section>

        <v-divider class="my-10"></v-divider>

        <section id="journals-section">
          <h2 id="journals" class="text-h4 mt-6 mb-3">11. Writing Journals & Notes</h2>
          <p>
            Sesplan provides a journaling system primarily linked to your characters, allowing for in-character diaries, GM notes for specific characters, or general logs related to them.
          </p>

          <v-list-item-title class="text-h5 my-3">11.1 Understanding Journals</v-list-item-title>
          <p>
            In the current version of Sesplan, journals are automatically created for each character you make. You don't manually create or delete the journal container itself. Instead, you manage the entries within these character-specific journals.
          </p>
          <ul class="my-3">
            <li>Navigate to "<strong>My Journals</strong>" from the main dashboard sidebar. This takes you to `JournalsView.vue`.</li>
            <li>This page lists all journals associated with your characters, displaying the journal's name (often derived from the character), the character's ID, and the journal's description (if any).</li>
            <li>From this list, you can click "<strong>View Entries</strong>" on any journal to navigate to its `JournalDetailView.vue`.</li>
          </ul>
          <p>
            Additionally, the "Journal" section within a <a href="#characters">Character's Detail Page</a> likely provides direct access to that character's journal entries.
          </p>

          <v-list-item-title class="text-h5 my-3">11.2 Managing Journal Entries</v-list-item-title>
          <p>
            The `JournalDetailView.vue` is where you manage the content of a specific journal. It displays the journal's name and description, and then lists all its entries.
          </p>
          <p>For each journal, you can perform the following actions on its entries:</p>
          <ul class="my-3">
            <li>
              <strong>Add New Entry:</strong>
              <ul>
                <li>Click the "<strong>Add Entry</strong>" button. This opens a modal dialog with the `JournalEntryForm.vue`.</li>
                <li>The form requires:
                  <ul>
                    <li><strong>Title (Optional):</strong> A title for your journal entry (e.g., "The Discovery in the Old Mill," "Negotiations with Baron Von Roth").</li>
                    <li><strong>Content (Required):</strong> The main body of your entry, written using a <a href="#markdown-editor">Markdown editor</a> for rich text formatting.</li>
                  </ul>
                </li>
                <li>Click "Add Entry" in the form to save it.</li>
              </ul>
            </li>
            <li class="mt-2">
              <strong>View Entries:</strong>
              <ul>
                <li>Entries are listed with their title and creation/update dates.</li>
                <li>A short preview of the Markdown content is often visible.</li>
                <li>You can expand each entry to view its full content rendered from Markdown.</li>
              </ul>
            </li>
            <li class="mt-2">
              <strong>Edit Entry:</strong>
              <ul>
                <li>Each entry in the list will have an "Edit" (pencil icon) button.</li>
                <li>Clicking it opens the `JournalEntryForm.vue` in the modal, pre-filled with the entry's current title and content, allowing you to make changes.</li>
              </ul>
            </li>
            <li class="mt-2">
              <strong>Delete Entry:</strong>
              <ul>
                <li>Each entry will have a "Delete" (trash icon) button.</li>
                <li>A confirmation dialog will appear before the entry is permanently removed.</li>
              </ul>
            </li>
          </ul>
          <p>
            The journaling system is focused on these individual entries within the character-bound journals.
            There is no current functionality to edit the overall journal's name or description directly from these views, as these are tied to the character.
          </p>
        </section>

        <v-divider class="my-10"></v-divider>

        <section id="settings-section">
          <h2 id="settings" class="text-h4 mt-6 mb-3">12. User Account Settings</h2>
          <p>
            You can manage your personal Sesplan account details through the User Settings page.
          </p>

          <v-list-item-title class="text-h5 my-3">12.1 Accessing User Settings</v-list-item-title>
          <p>
            To access your settings:
          </p>
          <ol class="mb-3">
            <li>Click on your username or avatar, which is typically located in the top-right corner of the application header.</li>
            <li>Select "<strong>Settings</strong>" from the dropdown menu.</li>
            <li>This will navigate you to the `SettingsView.vue` page.</li>
          </ol>

          <v-list-item-title class="text-h5 my-3">12.2 Configurable Settings</v-list-item-title>
          <p>
            The User Settings page is primarily divided into two sections:
          </p>
          <ul class="my-3">
            <li>
              <strong>Profile Information:</strong>
              <ul>
                <li><strong>First Name:</strong> You can update your first name here.</li>
                <li><strong>Last Name:</strong> You can update your last name here.</li>
                <li><strong>Email:</strong> Your registered email address is displayed but <em>cannot</em> be changed through this interface.</li>
                <li><strong>Username:</strong> Your username is displayed but <em>cannot</em> be changed after registration.</li>
                <li>Click the "<strong>Update Profile</strong>" button to save any changes made to your first or last name.</li>
              </ul>
            </li>
            <li class="mt-2">
              <strong>Change Password:</strong>
              <ul>
                <li>This section allows you to change your login password.</li>
                <li>You will need to provide your <strong>Current Password</strong>.</li>
                <li>Then, enter your <strong>New Password</strong>. It must be at least 8 characters long.</li>
                <li>Finally, <strong>Confirm New Password</strong> by re-entering it.</li>
                <li>Click the "<strong>Change Password</strong>" button to apply the new password.</li>
              </ul>
            </li>
          </ul>

          <v-list-item-title class="text-h5 my-3">12.3 Currently Unavailable Settings</v-list-item-title>
          <p>
            Please note that the following account management features are not currently available in the User Settings section:
          </p>
          <ul class="my-3">
            <li>Changing your email address.</li>
            <li>Changing your username.</li>
            <li>Deleting your account.</li>
            <li>Uploading a profile avatar or other interface/notification preferences.</li>
          </ul>
          <p>
            If you require assistance with actions not available through the interface, please refer to any support channels provided for the Sesplan application.
          </p>
        </section>

        <v-divider class="my-10"></v-divider>

        <section id="markdown-editor-section"> 
          <h3 id="markdown-editor" class="text-h5 mt-6 mb-3">13. A Note on the Markdown Editor</h3>
          <p>
            Throughout the Sesplan application, you will encounter <strong>Markdown editors</strong> for various text fields, such as descriptions for worlds, characters, items, campaign details, location descriptions, and journal entries. 
            Markdown is a lightweight markup language with plain-text-formatting syntax. It allows you to add formatting elements to plaintext text documents.
          </p>
          <p>
            Common formatting options you can use include:
          </p>
          <ul class="manual-list">
            <li><code># Heading 1</code>, <code>## Heading 2</code>, etc. for section titles.</li>
            <li><code>*italic*</code> or <code>_italic_</code> for <em>italicized text</em>.</li>
            <li><code>**bold**</code> or <code>__bold__</code> for <strong>bold text</strong>.</li>
            <li><code>- Unordered list item</code> or <code>* Unordered list item</code> for bullet points.</li>
            <li><code>1. Ordered list item</code> for numbered lists.</li>
            <li><code>[Link text](https://example.com)</code> for creating hyperlinks.</li>
            <li><code>`inline code`</code> for short code snippets or technical terms.</li>
            <li><code>```block code```</code> for longer code examples.</li>
          </ul>
          <p>
            Familiarizing yourself with basic Markdown syntax will help you create well-formatted and readable content within Sesplan. Most editors also provide a toolbar with common formatting options for ease of use.
          </p>
        </section>
        
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'ManualView',
  mounted() {
    document.title = 'User Manual | Sesplan';
  },
  methods: {
    scrollTo(id: string) {
      const element = document.getElementById(id);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }
});
</script>

<style scoped>
.manual-container {
  max-width: 900px; /* Or your preferred max-width */
}

.sticky-toc {
  position: sticky;
  top: 10px; /* Adjust as needed, for spacing from the top of the viewport */
  background-color: white; /* Ensure it has a background when floating */
  z-index: 1000; /* Keep it above other content */
  border-bottom: 1px solid #e0e0e0; /* Optional: add a subtle border when sticky */
}

section {
  /* margin-top: 2rem; */ /* Handled by dividers */
  /* margin-bottom: 2rem; */ /* Handled by dividers */
  padding-top: 1.5rem; /* Add some padding for scroll-to target */
}



p {
  margin-bottom: 1rem; /* Vuetify default is often less */
  line-height: 1.7;
  color: #4a4a4a; /* Slightly lighter than pure black for readability */
}

.table-of-contents ul {
  list-style: none;
  padding-left: 0;
}

.table-of-contents li {
  margin-bottom: 4px; /* Add some spacing between TOC items */
}

.table-of-contents li a {
  text-decoration: none;
  color: #1976D2; /* Vuetify primary color or your link color */
  cursor: pointer;
}

.table-of-contents li a:hover {
  text-decoration: underline;
}

.manual-list {
  padding-left: 20px; /* Standard padding for lists */
  margin-bottom: 1rem;
}

.manual-list li {
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

.manual-list ul {
  padding-left: 20px;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem; /* Add some bottom margin to nested lists */
}

.manual-list ul li {
  margin-bottom: 0.25rem; /* Tighter spacing for sub-list items */
}

/* Add more specific Vuetify component styling if needed */
</style> 