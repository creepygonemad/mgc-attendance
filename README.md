# Attendance Tracker Web Application

## Introduction
This project simplifies and enhances the user experience for tracking student attendance, addressing the limitations of my college’s attendance tracking system. By reimagining the data presentation and adding valuable metrics, this application provides a more intuitive, informative, and visually appealing interface.

---

## Key Differences Between College Website and My Application

### **College Website**
1. **Login Restrictions**:
   - Requires users to log in with a password in the specific format of the birthdate (YY-MM-DD).
   - Limited flexibility in password management.

2. **Attendance Data Presentation**:
   - Displays attendance in a basic tabular format with columns for:
     - Date.
     - Hours (Period 1, Period 2, Period 3, etc.).
     - Total Hours Present and Absent.
   - No overall attendance percentage provided.
   - Data is difficult to interpret and lacks actionable insights.

---

### **My Application**
1. **Enhanced User Interface**:
   - User-friendly login process.
   - Dashboard displays personalized student details, including:
     - **Name**.
     - **Department**, **Year**, and **Current Semester**.
     - **Overall Attendance Percentage**.

2. **Comprehensive Metrics and Visualization**:
   - **Pie Chart**: Visual representation of attendance percentage (Present vs. Absent).
   - Detailed data points include:
     - **Total Working Days**.
     - **Total Full Day Absences**.
     - **On-Duty Dates and Periods**.
     - **Partial Absences** (instances where students were present for part of the day).
     - **Full Day Absences with Dates**.
     - **Daily Attendance Details** with date-wise breakdown.

3. **Actionable Insights**:
   - Students can easily understand their attendance status and identify areas for improvement.
   - Simplifies communication between students and faculty regarding attendance-related queries.

---

## Features
- **Backend Framework**: Built with Flask for robust and scalable backend logic.
- **Web Scraping**: Automates the collection of attendance data from the college’s website.
- **Database Integration**: Efficient data storage and retrieval using SQL and ORM.
- **Dynamic Visualization**: Real-time generation of charts and metrics.
- **Responsive Design**: Ensures compatibility and usability on mobile devices and desktops.

---

## Benefits
- **Improved User Experience**: Simplifies the process of logging in and understanding attendance metrics.
- **Enhanced Data Representation**: Converts raw attendance data into meaningful insights and visualizations.
- **Empowered Students**: Provides a clear view of attendance, helping students stay informed and proactive.

---

## Installation and Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/attendance-tracker.git
   ```

2. Navigate to the project directory:
   ```bash
   cd attendance-tracker
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Access the application in your browser at:
   ```
   http://127.0.0.1:5000
   ```

---

## Screenshots
- **Login view on college site** :![mgc login portal](https://github.com/user-attachments/assets/eefef8e3-c9c6-4654-a344-010b04ba2c7a)

- **Login view on my site** :![my portal login](https://github.com/user-attachments/assets/fb23ccab-8585-46ff-9214-195240b9ccf5)

- **Dashboard of college site**:![mgc attendance show](https://github.com/user-attachments/assets/69432164-408a-4ff9-b6a9-593a48beb815)

- **Dashboard**: ![my site attendaceshow](https://github.com/user-attachments/assets/bedc0cec-28d6-4f63-998c-051245dc4893)

- **Detailed View**:![my site attendaceshow 2](https://github.com/user-attachments/assets/fd38fe07-60bf-43dc-bae5-5db6af322b04)


---

## Future Improvements
- Add support for mobile devices.
- Include faculty-facing features for better attendance management.
- Implement push notifications for low attendance warnings.

---

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests for enhancements and bug fixes.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contact
For any queries or suggestions, feel free to reach out:
- **Email**: prawink533@gmail.com
- **GitHub**: [Your GitHub Profile](https://github.com/yourusername)

