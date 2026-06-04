import { Spinner } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

export function LoadingSpinner() {
  const { t } = useTranslation();
  return (
    <div className="text-center py-5">
      <Spinner animation="border" role="status">
        <span className="visually-hidden">{t('common.loading')}</span>
      </Spinner>
    </div>
  );
}
