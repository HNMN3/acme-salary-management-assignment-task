import { Alert, Button } from "@mantine/core";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <Alert color="red" title="Something went wrong">
      {message}
      {onRetry && (
        <Button mt="sm" size="xs" variant="light" color="red" onClick={onRetry}>
          Retry
        </Button>
      )}
    </Alert>
  );
}
