from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, DateTime, Boolean, Integer

from src.aswwu.models.bases import NotificationsBase

#size is arbitrary for now until we decide on it

class Notification(NotificationsBase):
    notification_text = Column(String(500))
    notification_links = Column(String(500))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    severity = Column(Integer)
    visible = Column(Integer)

    def serialize(self):
        # determine if show_results field should be cast to a string
        return {
            'notification_text': self.notification_text,
            'notification_links': self.notification_links,
            'start_time': datetime.strftime(self.start_time, '%Y-%m-%d %H:%M:%S.%f'),
            'end_time': datetime.strftime(self.end_time, '%Y-%m-%d %H:%M:%S.%f'),
            'severity': self.severity,
            'visible': self.visible
        }