document.addEventListener('DOMContentLoaded', function() {
  const streamToggleBtn = document.querySelector('.stream-toggle-btn');
  const streamContainer = document.querySelector('.live-stream-feed');
  let eventSource = null;

  if (!streamToggleBtn || !streamContainer) return;

  streamToggleBtn.addEventListener('click', function() {
    this.classList.toggle('active');
    if (this.classList.contains('active')) {
      startStream();
    } else {
      stopStream();
    }
  });

  function startStream() {
    console.log('Stream started');
    streamContainer.innerHTML = '';
    eventSource = new EventSource('/api/events/stream');
    eventSource.onmessage = function(event) {
      const data = JSON.parse(event.data);
      appendEventToStream(data);
    };
    eventSource.onerror = function(error) {
      console.error('EventSource failed:', error);
      stopStream();
      streamToggleBtn.classList.remove('active');
    };
  }

  function stopStream() {
    console.log('Stream stopped');
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
  }

  function appendEventToStream(event) {
    const eventElement = document.createElement('div');
    eventElement.className = `stream-event event-${event.severity ? event.severity.toLowerCase() : 'info'}`;
    eventElement.innerHTML = `
      <div class="event-header">
        <span class="event-type"><i class="fas fa-info-circle"></i> ${event.event_type}</span>
        <span class="event-timestamp">${new Date(event.timestamp).toLocaleTimeString()}</span>
      </div>
      <div class="event-content">
        <p>${event.message}</p>
      </div>
    `;
    streamContainer.appendChild(eventElement);
    streamContainer.scrollTop = streamContainer.scrollHeight;
  }
});
