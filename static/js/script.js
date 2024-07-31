
function openPage(evt, pageName) {
    var i, tabcontent, tablinks;

    // Hide all elements with class="tabcontent" by default */
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Remove the background color of all tablinks/buttons
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(pageName).style.display = "block";
    evt.currentTarget.className += " active";
}

// Get the element with id="defaultOpen" and click on it to open the default tab
document.getElementById("defaultOpen").click();


document.addEventListener('DOMContentLoaded', () => {
    const calendarDates = document.querySelector('.calendar-dates');
    const monthYearDisplay = document.querySelector('.month-year');
    const prevMonthButton = document.querySelector('.prev-month');
    const nextMonthButton = document.querySelector('.next-month');

    let currentDate = new Date();
    currentDate.setDate(1);

    function renderCalendar() {
        const month = currentDate.getMonth();
        const year = currentDate.getFullYear();
        const firstDayIndex = currentDate.getDay();
        const lastDay = new Date(year, month + 1, 0).getDate();
        const prevLastDay = new Date(year, month, 0).getDate();
        const lastDayIndex = new Date(year, month + 1, 0).getDay();
        const nextDays = 7 - lastDayIndex - 1;

        monthYearDisplay.innerText = `${currentDate.toLocaleString('default', { month: 'long' })} ${year}`;

        let days = '';

        for (let x = firstDayIndex; x > 0; x--) {
            days += `<div class="prev-date">${prevLastDay - x + 1}</div>`;
        }

        for (let i = 1; i <= lastDay; i++) {
            const day = new Date(year, month, i);
            const isBooked = checkIfBooked(day);
            days += `<div class="${isBooked ? 'booked' : 'available'}">${i}</div>`;
        }

        for (let j = 1; j <= nextDays; j++) {
            days += `<div class="next-date">${j}</div>`;
        }

        calendarDates.innerHTML = days;
    }

    function checkIfBooked(date) {
        // Example: all dates after today are booked for demonstration purposes
        return date >= new Date();
    }

    prevMonthButton.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    nextMonthButton.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    renderCalendar();
});
